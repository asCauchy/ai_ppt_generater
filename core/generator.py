import os
from openai import OpenAI


class PPTGenerator:

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError("请设置环境变量 DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model = "deepseek-chat"
        self._prompts = {}

    def load_prompts(self, prompts_dir):
        for name in ["system", "json_schema", "styles", "rules"]:
            path = os.path.join(prompts_dir, f"{name}.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self._prompts[name] = f.read()

    def generate(self, topic, style, pages, temperature=0.2, max_tokens=8192):
        system = "\n\n".join([
            self._prompts.get("system", ""),
            self._prompts.get("styles", ""),
            self._prompts.get("rules", ""),
            self._prompts.get("json_schema", ""),
        ])

        user = f"主题：{topic}\n风格：{style}\n页数：{pages}\n\n请严格按照上述JSON Schema输出PPT结构。"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
