import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.pipeline import PresentationPipeline, PipelineError
from core.validator import PresentationValidator
from core.formatters import get_formatter, FORMATTERS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    debug = "--debug" in sys.argv
    if debug:
        sys.argv.remove("--debug")

    prompts_dir = os.path.join(SCRIPT_DIR, "prompts")
    schema_path = os.path.join(SCRIPT_DIR, "schemas", "presentation_schema.json")
    output_dir = os.path.join(SCRIPT_DIR, "outputs")

    # ---- 用户输入 ----
    print("=" * 50)
    print("  Presentation OS — Multi-Agent Pipeline")
    print("=" * 50)

    topic = input("请输入主题: ").strip()
    style = input("请输入风格 (学术风/商务风/科技风/党政风): ").strip()
    pages = input("请输入页数: ").strip()
    audience = input("请输入听众画像 (如: 计算机专业大三学生): ").strip()
    occasion = input("请输入场合 (如: classroom_lecture/academic_defense): ").strip()
    goal = input("请输入主要目标 (inform/persuade/inspire/instruct/report): ").strip()
    total_min = input("请输入演示时长(分钟, 默认=页数×2): ").strip()
    fmt_choice = input(f"输出格式 ({'/'.join(FORMATTERS.keys())}, 默认md): ").strip() or "md"

    if not all([topic, style, pages]):
        print("错误: 主题、风格、页数不能为空")
        sys.exit(1)

    try:
        pages_int = int(pages)
    except ValueError:
        print("错误: 页数必须为数字")
        sys.exit(1)

    duration_min = int(total_min) if total_min else pages_int * 2

    # Build context overrides
    context_overrides = {
        "audience": {"profile": audience or "通用听众"},
        "occasion": {"type": occasion or "classroom_lecture"},
        "intent": {"primary_goal": goal or "inform"},
        "duration": {"total_minutes": duration_min},
    }

    try:
        # ---- Init Pipeline ----
        validator = PresentationValidator(schema_path)
        pipeline = PresentationPipeline(
            validator=validator,
            prompts_dir=prompts_dir,
            debug=debug,
        )

        # ---- Run ----
        if debug:
            print("\n[debug] Debug Snapshot 已启用 — state 将保存至 debug/run_NN/")
        print("\n启动 Multi-Agent Pipeline...")
        state = pipeline.run(
            topic=topic,
            style=style,
            pages=pages_int,
            context=context_overrides,
        )

        # ---- Format Output ----
        fmt = get_formatter(fmt_choice)
        output = fmt.format(state)
        path = fmt.save(output, output_dir)

        print(f"\n{'=' * 50}")
        print(f"Pipeline 完成。输出: {path}")
        print(f"State stage: {state.get('runtime', {}).get('generation_stage', 'unknown')}")
        print(f"Agents: {state.get('runtime', {}).get('agents_involved', [])}")

    except PipelineError as e:
        print(f"\nPipeline 失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
