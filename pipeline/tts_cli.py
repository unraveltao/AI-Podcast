"""IndexTTS 2.5 的命令行入口 —— 我们自己的，不走官方 cli_v2。

为什么不修官方的 cli_v2
-----------------------
`indextts/cli_v2.py` 是给 IndexTTS 2.0 写的，跟 2.5 的 API 有三处对不上：

  1. `_load_indextts2()` 导入的是 `indextts.infer_v2.IndexTTS2`（2.0 的类），
     它构造时会去读 `cfg.dataset["bpe_model"]` —— 2.5 改用 tiktoken，根本没有这个文件。
  2. 2.0 的类收 `use_fp16`，2.5 的类收 `use_bf16`，参数名不一样。
  3. 2.5 的 `infer()` 多了一个必填的 `lang` 参数，cli_v2 不传，一调就报 TypeError。

改这三处等于替上游维护一个分叉，他们一升级就全废。所以这里自己写一层薄封装：
只做「参数解析 → 调 IndexTTS2 → 落盘」，逻辑跟将来的 tts_adapter 完全一致。

用法（必须用 IndexTTS 自己的 venv 解释器）
------------------------------------------
  E:\\Apps\\AI\\Index_tts2.5\\.venv\\Scripts\\python.exe pipeline/tts_cli.py \\
      --text "你好，欢迎来到今天的心理学播客。" \\
      --voice content/media/voice-samples/xxx.wav \\
      --output pipeline/outputs/_smoke/raw_test.wav

  # 长文本从文件读
  ... --text-file script.txt --voice ref.wav --output out.wav
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_settings() -> dict:
    cfg = ROOT / "pipeline" / "config" / "settings.yaml"
    if not cfg.is_file():
        return {}
    import yaml

    return yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}


def _resolve(path_str: str | None, default: str | None = None) -> Path:
    raw = path_str or default
    if not raw:
        raise ValueError("路径为空")
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p)


def main() -> int:
    settings = _load_settings()
    indextts_cfg = (settings.get("engines") or {}).get("indextts") or {}

    ap = argparse.ArgumentParser(description="IndexTTS 2.5 单段合成")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="要合成的文本")
    src.add_argument("--text-file", help="UTF-8 文本文件")
    ap.add_argument("--voice", required=True, help="参考音频路径（说话人音色来源）")
    ap.add_argument("--output", required=True, help="输出 wav 路径")
    ap.add_argument("--lang", default="zh", help="语言代码：zh / en / ja / yue …（默认 zh）")
    ap.add_argument("--emotion-text", help="情绪描述，如「疲惫、压低声音」。启用会额外加载 QwenEmotion")
    ap.add_argument("--emotion-weight", type=float, default=0.8, help="情绪强度 0–1（默认 0.8）")
    ap.add_argument("--device", default=indextts_cfg.get("device", "cuda:0"))
    ap.add_argument("--model-dir", default=indextts_cfg.get("model_dir"))
    ap.add_argument("--bf16", dest="bf16", action="store_true", default=bool(indextts_cfg.get("fp16", True)))
    ap.add_argument("--no-bf16", dest="bf16", action="store_false")
    ap.add_argument("--force", action="store_true", help="输出已存在时覆盖")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    text = args.text if args.text else Path(args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        print("ERROR: 文本为空", file=sys.stderr)
        return 2

    voice = _resolve(args.voice)
    if not voice.is_file():
        print(f"ERROR: 参考音频不存在：{voice}", file=sys.stderr)
        return 2

    output = _resolve(args.output)
    if output.exists() and not args.force:
        print(f"ERROR: 输出已存在，加 --force 覆盖：{output}", file=sys.stderr)
        return 2

    model_dir = _resolve(args.model_dir, indextts_cfg.get("model_dir"))
    cfg_path = model_dir / "config.yaml"
    if not cfg_path.is_file():
        print(f"ERROR: 模型目录里没有 config.yaml：{cfg_path}", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)

    # 延迟导入：--help 不该拖起 torch
    from indextts.infer_v2_5 import IndexTTS2

    t0 = time.time()
    print(f"[1/2] 加载模型  {model_dir}")
    tts = IndexTTS2(
        cfg_path=str(cfg_path),
        model_dir=str(model_dir),
        use_bf16=args.bf16,
        device=args.device,
        use_qwen_emo=bool(args.emotion_text),   # 只在要情绪描述时才多加载一个模型
    )
    print(f"      加载耗时 {time.time() - t0:.1f}s，设备 {tts.device}，bf16={tts.use_bf16}")

    t1 = time.time()
    print(f"[2/2] 合成  {len(text)} 字")
    tts.infer(
        spk_audio_prompt=str(voice),
        text=text,
        output_path=str(output),
        lang=args.lang,
        use_emo_text=bool(args.emotion_text),
        emo_text=args.emotion_text,
        emo_alpha=args.emotion_weight,
        verbose=args.verbose,
    )

    if not output.is_file():
        print(f"ERROR: 合成结束但没生成文件：{output}", file=sys.stderr)
        return 4

    size_kb = output.stat().st_size / 1024
    print(f"      合成耗时 {time.time() - t1:.1f}s")
    print(f"完成 → {output}  ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(4)
