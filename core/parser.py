import json
import re


class PPTParseError(Exception):
    pass


class PPTParser:

    def parse(self, raw_text):
        raw = raw_text.strip()

        # 1) 直接 JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 2) ```json ... ``` 代码块
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3) 从文本中提取最外层 {...}
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

        raise PPTParseError(
            "无法从API响应中提取有效JSON。请重试。\n"
            f"原始响应前500字: {raw[:500]}"
        )
