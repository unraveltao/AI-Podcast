"""音频归一化：把任意格式的素材整理成管线能吃的规格。

为什么需要它
------------
素材来源五花八门：网页录音的 mp3、手机 m4a、别人给的 wav、RVC 吐的 40k wav。
采样率、声道数、位深、响度、首尾静音全都不一样。管线里每一步都假设固定的格式，
所以在进入管线之前统一一次，比在每个模块里各自兼容要省事得多。

三种规格
--------
  reference  IndexTTS 的参考音频。单声道、48 kHz、16 bit，掐掉首尾静音。
             默认**不做响度归一** —— 参考音只提供音色，动响度会改变模型对音色的判断。
  voice      送进 RVC 的干声。单声道、48 kHz、16 bit，同样掐静音。
  final      要发布的成品。单声道、44.1 kHz、16 bit，按 -16 LUFS 做响度归一。

用法
----
  python pipeline/audio_prep.py probe     素材.mp3
  python pipeline/audio_prep.py reference 素材.mp3 输出.wav
  python pipeline/audio_prep.py voice     raw.wav   converted_in.wav
  python pipeline/audio_prep.py final     整集.wav  EP001.mp3

注意：这个脚本只需要 ffmpeg，不需要 torch。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# 项目根 = 本文件所在目录的上一级
ROOT = Path(__file__).resolve().parent.parent

# 每种模式的 ffmpeg 参数
#   loudnorm        无条件应用的响度目标（None = 默认不做）
#   loudnorm_opt_in 加了 --loudnorm 时用的目标
MODES = {
    "reference": {
        "sample_rate": 48000,
        "codec": ["-c:a", "pcm_s16le"],
        "trim": True,
        "loudnorm": None,
        # 参考音只提音量到"够响但不压动态"，-20 LUFS 比成品松一档
        "loudnorm_opt_in": "I=-20:TP=-2:LRA=7",
    },
    "voice": {
        "sample_rate": 48000,
        "codec": ["-c:a", "pcm_s16le"],
        "trim": True,
        "loudnorm": None,
        "loudnorm_opt_in": "I=-20:TP=-2:LRA=7",
    },
    "final": {
        "sample_rate": 44100,
        "codec": ["-c:a", "pcm_s16le"],
        "trim": False,
        "loudnorm": "I=-16:TP=-1.5:LRA=11",
        "loudnorm_opt_in": "I=-16:TP=-1.5:LRA=11",
    },
}

# 掐首尾静音：正向掐头 → 反转 → 再掐头（等于掐尾）→ 反转回来
TRIM_FILTER = (
    "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,"
    "areverse,"
    "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,"
    "areverse"
)


def _settings_ffmpeg() -> str:
    """从 settings.yaml 读 ffmpeg 路径，读不到就用 PATH 上的。"""
    cfg = ROOT / "pipeline" / "config" / "settings.yaml"
    try:
        import yaml

        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        path = (data.get("tools") or {}).get("ffmpeg")
        if path:
            p = Path(path)
            if not p.is_absolute():
                p = ROOT / p
            if p.is_file():
                return str(p)
    except Exception:
        pass
    return shutil.which("ffmpeg") or "ffmpeg"


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def probe(src: Path) -> dict:
    """读音频参数。用 ffprobe，拿不到就抛错。"""
    ffprobe = _settings_ffmpeg().replace("ffmpeg", "ffprobe")
    if not Path(ffprobe).is_file():
        ffprobe = shutil.which("ffprobe") or "ffprobe"

    cp = _run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration,size,bit_rate",
            "-show_entries", "stream=codec_name,sample_rate,channels,channel_layout",
            "-of", "json", str(src),
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(f"ffprobe 读不了这个文件：{src}\n{cp.stderr.strip()}")

    data = json.loads(cp.stdout)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {
        "path": str(src),
        "duration_sec": round(float(fmt.get("duration", 0) or 0), 3),
        "size_mb": round(float(fmt.get("size", 0) or 0) / 1048576, 2),
        "bit_rate_kbps": round(float(fmt.get("bit_rate", 0) or 0) / 1000),
        "codec": stream.get("codec_name"),
        "sample_rate": int(stream.get("sample_rate", 0) or 0),
        "channels": int(stream.get("channels", 0) or 0),
        "channel_layout": stream.get("channel_layout"),
    }


def normalize(src: Path, dst: Path, mode: str, loudnorm: bool = False, highpass: int | None = None) -> dict:
    """按 mode 把 src 转成 dst。返回转换前后的参数，方便记日志。"""
    if mode not in MODES:
        raise ValueError(f"未知模式：{mode}，可选 {list(MODES)}")
    if not src.is_file():
        raise FileNotFoundError(f"输入文件不存在：{src}")

    spec = MODES[mode]
    before = probe(src)

    filters: list[str] = []
    if highpass:
        # 切掉 80 Hz 以下的隆隆声和桌面震动，说话声不会受损
        filters.append(f"highpass=f={highpass}")
    if spec["trim"]:
        filters.append(TRIM_FILTER)

    # reference/voice 默认不归响度，加 --loudnorm 才做
    target = spec["loudnorm_opt_in"] if loudnorm else spec["loudnorm"]
    if target:
        filters.append(f"loudnorm={target}")

    filters.append(f"aresample={spec['sample_rate']}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _settings_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-vn", "-ac", "1", "-ar", str(spec["sample_rate"]),
        "-af", ",".join(filters),
        *spec["codec"],
        str(dst),
    ]
    cp = _run(cmd)
    if cp.returncode != 0:
        raise RuntimeError(f"ffmpeg 转换失败：\n{' '.join(cmd)}\n{cp.stderr.strip()}")

    after = probe(dst)
    return {"mode": mode, "before": before, "after": after}


def _print_probe(info: dict) -> None:
    print(f"  文件      {info['path']}")
    print(f"  时长      {info['duration_sec']} 秒")
    print(f"  编码      {info['codec']}  {info['sample_rate']} Hz  {info['channels']} 声道 ({info['channel_layout']})")
    print(f"  大小      {info['size_mb']} MB   {info['bit_rate_kbps']} kbps")


def main() -> int:
    ap = argparse.ArgumentParser(description="音频归一化（IndexTTS 参考音 / RVC 输入 / 成品）")
    ap.add_argument("mode", choices=["probe", "reference", "voice", "final"])
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path, nargs="?")
    ap.add_argument("--loudnorm", action="store_true", help="reference/voice 模式也做响度归一")
    ap.add_argument("--highpass", type=int, metavar="HZ", help="加高通滤波，建议 80（去掉低频隆隆声）")
    args = ap.parse_args()

    if args.mode == "probe":
        _print_probe(probe(args.src))
        return 0

    if args.dst is None:
        ap.error(f"{args.mode} 模式需要指定输出路径")

    result = normalize(args.src, args.dst, args.mode, loudnorm=args.loudnorm, highpass=args.highpass)
    print(f"[{args.mode}] 转换完成")
    print("  转换前：")
    _print_probe(result["before"])
    print("  转换后：")
    _print_probe(result["after"])
    print(f"  → {args.dst}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
