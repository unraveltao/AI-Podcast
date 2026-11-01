"""Applio RVC 单段转换 CLI。

必须用 **Applio 自带的解释器**跑（它有 torch 2.11 + cu128）：

  pipeline/engines/applio/env/python.exe pipeline/rvc_cli.py \
      --input  pipeline/outputs/_smoke/raw_test_short.wav \
      --output pipeline/outputs/_smoke/converted_test.wav \
      --model  pipeline/engines/rvc-models/yelan/yelan.pth \
      --index  pipeline/engines/rvc-models/yelan/yelan_added_IVF444_Flat_nprobe_1_yelan_v2.index

为什么走 Python API 而不是点 Gradio
-----------------------------------
Applio 的 core.py 里 `run_infer_script()` 收全部参数，比驱动网页稳得多，
也不用常驻一个 Gradio 进程抢显存。任务书 7.2 要求的「优先 CLI」就是这个意思。

注意
----
- 输出路径必须以 .wav 结尾，Applio 内部靠字符串替换决定扩展名。
- 采样率由模型决定（这两个模型都是 40k），不要在这里指定，指定了会被忽略。
- 转换前建议先过一遍 audio_prep.py voice，把输入统一成 48k 单声道。
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPLIO_ROOT = ROOT / "pipeline" / "engines" / "applio"


def _resolve(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p)


def main() -> int:
    ap = argparse.ArgumentParser(description="Applio RVC 单段转换")
    ap.add_argument("--input", required=True, help="输入 wav")
    ap.add_argument("--output", required=True, help="输出 wav（必须以 .wav 结尾）")
    ap.add_argument("--model", required=True, help=".pth 路径")
    ap.add_argument("--index", default="", help=".index 路径，可留空")
    ap.add_argument("--pitch", type=int, default=0, help="变调半音：同性别 0，男→女 +12")
    ap.add_argument("--index-rate", type=float, default=0.6, help="0.5–0.75")
    ap.add_argument("--protect", type=float, default=0.33, help="别超过 0.5")
    ap.add_argument("--f0-method", default="rmvpe", choices=["rmvpe", "fcpe", "swift"])
    ap.add_argument("--volume-envelope", type=float, default=1.0, help="1.0 = 不压动态")
    ap.add_argument("--embedder", default="contentvec")
    args = ap.parse_args()

    src = _resolve(args.input)
    dst = _resolve(args.output)
    model = _resolve(args.model)
    index = _resolve(args.index) if args.index else ""

    for label, p in (("输入音频", src), ("模型", model)):
        if not Path(p).is_file():
            print(f"ERROR: {label}不存在：{p}", file=sys.stderr)
            return 2
    if index and not Path(index).is_file():
        print(f"ERROR: 索引文件不存在：{index}", file=sys.stderr)
        return 2
    if dst.suffix.lower() != ".wav":
        print("ERROR: --output 必须以 .wav 结尾（Applio 靠它判断扩展名）", file=sys.stderr)
        return 2
    if dst.exists():
        print(f"ERROR: 输出已存在，先删掉：{dst}", file=sys.stderr)
        return 2

    dst.parent.mkdir(parents=True, exist_ok=True)

    # core.py 依赖工作目录下的相对路径，必须切到 Applio 根目录再导入
    os.chdir(APPLIO_ROOT)
    sys.path.insert(0, str(APPLIO_ROOT))
    import core  # noqa: E402

    t0 = time.time()
    print(f"[1/1] 转换  {src.name}  →  {dst.name}")
    print(f"      模型 {model.name}  f0={args.f0_method}  pitch={args.pitch}  "
          f"index_rate={args.index_rate}  protect={args.protect}")

    msg, out = core.run_infer_script(
        pitch=args.pitch,
        index_rate=args.index_rate,
        volume_envelope=args.volume_envelope,
        protect=args.protect,
        f0_method=args.f0_method,
        input_path=str(src),
        output_path=str(dst),
        pth_path=str(model),
        index_path=str(index) if index else "",
        f0_autotune=False,
        f0_autotune_strength=0.0,
        proposed_pitch=False,
        proposed_pitch_threshold=0.0,
        export_format="WAV",
        embedder_model=args.embedder,
    )

    out_path = Path(out)
    if not out_path.is_file():
        print(f"ERROR: 转换结束但没生成文件：{out_path}", file=sys.stderr)
        return 4

    print(f"      {msg}")
    print(f"      耗时 {time.time() - t0:.1f}s  →  {out_path}  "
          f"({out_path.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(4)
