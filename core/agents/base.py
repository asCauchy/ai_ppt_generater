"""BaseAgent — every agent in the Presentation Pipeline inherits from this.

Responsibilities:
  1. Load its system prompt from prompts/agents/<name>.txt
  2. Execute (call LLM) and return a state diff
  3. Attach provenance metadata to every slide it touches
  4. Append an entry to runtime.history
  5. Optionally enforce its write contract
"""

from __future__ import annotations
import os
import copy
from datetime import datetime, timezone

from openai import OpenAI

from .contracts import get_contract


class AgentError(Exception):
    pass


class BaseAgent:
    name: str = ""
    version: str = "v1"
    model: str = "deepseek-chat"
    temperature: float = 0.2
    max_tokens: int = 8192
    max_retries: int = 2

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set. Set the environment variable or pass api_key parameter.")
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.contract = get_contract(self.name)
        self._system_prompt = ""

    # ---- public API ----

    def load_prompt(self, prompts_dir: str):
        """Load system prompt from prompts/agents/<name>.txt"""
        path = os.path.join(prompts_dir, "agents", f"{self.name}.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._system_prompt = f.read()

    def run(self, state: dict, feedback: list = None) -> dict:
        """Execute agent and return a state diff (only modified subtrees)."""
        user_prompt = self._build_user_prompt(state, feedback)
        raw = self._call_api(user_prompt)
        parsed = self._parse_response(raw)
        diff = self._attach_provenance(parsed, state)
        diff = self._attach_history(diff, state)
        diff.setdefault("runtime", {})
        diff["runtime"]["generation_stage"] = self._stage_name()
        return diff

    # ---- subclasses override these ----

    def _build_user_prompt(self, state: dict, feedback: list = None) -> str:
        raise NotImplementedError

    def _stage_name(self) -> str:
        """Maps to runtime.generation_stage value."""
        return self.name.replace("_", "") + "ed"

    # ---- internal ----

    def _call_api(self, user_prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content

    def _parse_response(self, raw: str) -> dict:
        """JSON extraction with fallback (same 3-tier strategy as PPTParser)."""
        import json
        import re

        raw = raw.strip()

        # 1) direct
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 2) code block
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3) regex extract
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

        raise AgentError(f"[{self.name}] 无法从响应中提取 JSON。前500字: {raw[:500]}")

    def _attach_provenance(self, diff: dict, state: dict) -> dict:
        """Stamp provenance on every slide the agent created or modified."""
        now = _utcnow()
        agent_id = f"{self.name}_{self.version}"

        slides = diff.get("slides", [])
        for i, slide in enumerate(slides):
            prov = slide.setdefault("provenance", {})
            existing_slide = self._find_existing_slide(state, slide)
            if existing_slide:
                prov.setdefault("generated_by", existing_slide.get("provenance", {}).get("generated_by", agent_id))
                prov.setdefault("generated_at", existing_slide.get("provenance", {}).get("generated_at", now))
                revised = list(prov.get("revised_by", []))
                if agent_id not in revised:
                    revised.append(agent_id)
                prov["revised_by"] = revised
            else:
                prov["generated_by"] = agent_id
                prov["generated_at"] = now
                prov["revised_by"] = prov.get("revised_by", [])

        return diff

    def _attach_history(self, diff: dict, state: dict) -> dict:
        now = _utcnow()
        entry = {
            "action": self._stage_name(),
            "agent": f"{self.name}_{self.version}",
            "timestamp": now,
            "summary": self._history_summary(diff),
        }
        runtime = diff.setdefault("runtime", {})
        runtime.setdefault("agents_involved", list(state.get("runtime", {}).get("agents_involved", [])))
        if f"{self.name}_{self.version}" not in runtime["agents_involved"]:
            runtime["agents_involved"] = runtime["agents_involved"] + [f"{self.name}_{self.version}"]
        history = list(state.get("runtime", {}).get("history", [])) + [entry]
        runtime["history"] = history
        return diff

    def _history_summary(self, diff: dict) -> str:
        """One-line summary of what this agent did. Override in subclasses."""
        slides = diff.get("slides", [])
        sections = diff.get("narrative_arc", {}).get("sections", [])
        if slides:
            return f"{self.name} modified {len(slides)} slides"
        if sections:
            return f"{self.name} planned {len(sections)} sections"
        return f"{self.name} executed"

    def _find_existing_slide(self, state: dict, slide: dict):
        """Find an existing slide by index or id for provenance tracking."""
        sid = slide.get("id")
        idx = slide.get("index")
        for s in state.get("slides", []):
            if sid and s.get("id") == sid:
                return s
            if idx is not None and s.get("index") == idx:
                return s
        return None

    def _strip_diff(self, diff: dict) -> dict:
        """Remove fields not in the agent's write contract (light enforcement)."""
        allowed = self.contract.get("write_paths", [])
        return _filter_by_paths(diff, allowed)


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_by_paths(obj, paths, prefix=""):
    """Keep only keys whose dotted path matches one of the allowed paths."""
    if not isinstance(obj, dict):
        return obj
    result = {}
    for key, value in obj.items():
        full = f"{prefix}.{key}" if prefix else key
        if _path_matches(full, paths):
            if isinstance(value, dict):
                result[key] = _filter_by_paths(value, paths, full)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                result[key] = [_filter_by_paths(item, paths, full.replace("[*]", f"[{item.get('index', i)}]")) for i, item in enumerate(value)]
            else:
                result[key] = value
    return result


def _path_matches(path: str, allowed: list[str]) -> bool:
    import fnmatch
    for pattern in allowed:
        if fnmatch.fnmatch(path, pattern):
            return True
        # Also match prefix: "slides[*]" should match "slides[0].title"
        if path.startswith(pattern.rstrip("*").rstrip("[").rstrip("]")):
            return True
        # Direct equality
        if path == pattern:
            return True
    return False
