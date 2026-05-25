# AI PPT 结构生成器

基于 DeepSeek API 自动生成结构化 PPT JSON，支持 Markdown / HTML / PPTX 多格式导出。

## 项目结构

```
ai_ppt_generator/
├── main.py                   # CLI 入口
├── prompts/
│   ├── system.txt            # 系统角色定义
│   ├── json_schema.txt       # JSON 输出 Schema 指令（硬约束）
│   ├── styles.txt            # 4 种风格预设
│   └── rules.txt             # 结构/内容/视觉规则
├── core/
│   ├── generator.py          # DeepSeek API 调用（temperature=0.2 保证稳定性）
│   ├── parser.py             # JSON 提取器（3 层容错）
│   ├── validator.py          # 结构校验器（15+ 条规则）
│   ├── formatter.py          # 向后兼容包装器
│   └── formatters/
│       ├── __init__.py       # 格式化器注册表
│       ├── base.py           # 抽象基类
│       ├── markdown.py       # Markdown 输出
│       ├── html.py           # HTML 输出（含内联 CSS）
│       └── pptx.py           # PPTX 输出（需 python-pptx）
├── outputs/                  # 输出目录
├── schemas/
│   └── ppt_schema.json       # JSON Schema 定义
├── tests/
│   └── cases.json            # 5 组测试用例
└── README.md
```

## 数据流

```
prompts/*.txt ──┐
                ├──→ [Generator] ──API(t=0.2)──→ JSON 字符串
                │         ↑                              ↓
user input ─────┘    OpenAI SDK                  [Parser] 3层容错提取
                                              ├─ 直接 parse
                                              ├─ ```json``` 代码块
                                              └─ 正则提取 {...}
                                                       ↓
                                              dict ──→ [Validator]
                                                        ├─ 必填字段
                                                        ├─ page_number 连续性
                                                        ├─ type 合法性
                                                        ├─ 首尾页类型
                                                        └─ content 行数
                                                       ↓
                                              [Formatter] ──→ outputs/*.md
                                                        ├──→ outputs/*.html
                                                        └──→ outputs/*.pptx
```

## 快速开始

```bash
# 安装依赖
pip install openai

# 可选：HTML/PPTX 输出
pip install python-pptx

# 设置 API Key
# Linux/macOS:  export DEEPSEEK_API_KEY="sk-xxx"
# Windows PS:   $env:DEEPSEEK_API_KEY="sk-xxx"

# 运行
python main.py
```

## 设计原则

| 原则 | 实现 |
|------|------|
| **稳定 JSON 输出** | system prompt 内含 Schema 指令，temperature=0.2 |
| **Parser 容错** | 3 层提取策略：裸 JSON → markdown 代码块 → 正则兜底 |
| **校验先行** | 15+ 校验规则，发现问题可拒绝保存 |
| **格式可扩展** | `formatters/` 插件体系，注册新格式只需实现 `BaseFormatter` |
| **职责分离** | Generator/Parser/Validator/Formatter 各自独立 |

## 添加新输出格式

1. 在 `core/formatters/` 新建文件
2. 继承 `BaseFormatter`，实现 `format(self, ppt_data) -> str|bytes`
3. 在 `core/formatters/__init__.py` 注册

```python
from .pdf import PDFFormatter
FORMATTERS["pdf"] = PDFFormatter
EXTENSIONS["pdf"] = ".pdf"
```
