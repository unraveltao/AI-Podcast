# pipeline —— 实现端

把「剧本 YAML + 角色配置」变成「一整集音频」的地方。只做音频生产，不做发布、不做运营。

**当前状态**：阶段一（环境检查）已完成，代码尚未开始写。详见 [`docs/environment-report.md`](docs/environment-report.md)。

---

## 目录

```text
pipeline/
├── tts_cli.py            ✅ 已完成  单段合成入口（替代官方 cli_v2，原因见 docs 3.3）
├── audio_prep.py         ✅ 已完成  音频归一化：任意格式 → 参考音 / 干声 / 成品
├── main.py                          # 整集入口：--script scripts/EP001.yaml
├── orchestrator.py                  # 读配置 → 逐段调度 → 记状态
├── tts_adapter.py                   # 复用 tts_cli 的逻辑，进程内常驻模型
├── rvc_adapter.py                   # 调 Applio，把 raw 换成目标音色
├── audio_composer.py                # 拼接 / 静音 / 归一 / 导出 wav、mp3
├── validators.py                    # 剧本与模型文件校验
├── config/
│   ├── settings.yaml          # 全局设置：引擎路径、音频参数、重试策略
│   └── characters.yaml        # 角色 → 参考音频 / RVC 模型 / 转换参数（唯一事实来源）
├── scripts/                   # 每集一份剧本 YAML（ChatGPT 写），格式见该目录 README
├── engines/
│   ├── rvc-models/            # RVC 音色模型 .pth + .index（不进 git）
│   └── applio/                # Applio 本体，阶段二装到这里（不进 git）
├── outputs/                   # 产物：raw / converted / final（不进 git）
├── logs/                      # 运行日志与中间记录（不进 git）
├── tests/                     # 各模块独立测试
└── docs/
    └── environment-report.md
```

代码文件放在 `pipeline/` 根下，不再套一层 `pipeline/pipeline/` —— 目录名和包名重名只会让人多打一次字。

**IndexTTS 不在这里。** 它已经在 `E:\Apps\AI\Index_tts2.5` 跑通，按开发原则不搬、不复制，
路径写在 `config/settings.yaml` 的 `engines.indextts` 下。

---

## 为什么引擎和模型都塞在 `engines/`

为了让整个实现端能被打包带走：`engines/` 里放的是"换台机器也要跟着走"的东西
（Applio 本体 + 音色模型），代码和配置在它旁边，`settings.yaml` 里记着 IndexTTS 的外部路径。

真正的瓶颈在 IndexTTS —— 它有 4 GB 权重和独立 venv，目前不在包内。
如果哪天要做成完全自包含的安装包，得把 IndexTTS 也搬进 `engines/`，并改 `settings.yaml` 一处。

---

## 数据流

```text
scripts/EPxxx.yaml
        │
        ├─ 校验：字段、speaker、参考音频、模型文件
        ▼
   tts_adapter ──► outputs/EPxxx/raw/EPxxx-001-raw.wav
        │           （IndexTTS2 直接 import，不用 CLI —— 原因见环境报告 3.3）
        ▼
   rvc_adapter ──► outputs/EPxxx/converted/EPxxx-001-converted.wav
        │           （Applio，阶段二之后接）
        ▼
 audio_composer ─► outputs/EPxxx/final/EPxxx.wav
        │             EPxxx.mp3
        ▼
    FFmpeg：拼接 / 补静音 / 统一采样率 / 响度归一 / 转码
```

串行执行，不做并发 —— 8 GB 显存装不下两个引擎同时在线。

---

## 现在能跑什么

必须用 **IndexTTS 的 venv 解释器**（系统 `python` 是 Store 占位符，跑不了）：

```powershell
$PY = "E:\Apps\AI\Index_tts2.5\.venv\Scripts\python.exe"

# 1) 看一个音频文件的规格
& $PY pipeline/audio_prep.py probe "D:\某处\录音.mp3"

# 2) 归一化成 IndexTTS 的参考音频（48k 单声道，掐首尾静音）
& $PY pipeline/audio_prep.py reference "D:\某处\录音.mp3" content/media/voice-samples/xxx.wav

# 3) 合成一段
& $PY pipeline/tts_cli.py --text "今天我们来聊一聊焦虑。" `
    --voice content/media/voice-samples/narrator-selfrecorded.wav `
    --output pipeline/outputs/_smoke/raw_test.wav
```

**跑之前先把 7860 上的 IndexTTS WebUI 关掉。** 实测开着它会让合成慢 70 倍（RTF 25 → 2.2）。

---

## 还没做的部分

| 模块 | 状态 |
|---|---|
| `tts_cli.py` | ✅ 已完成，实测 RTF 2.2 |
| `audio_prep.py` | ✅ 已完成，三种规格（reference / voice / final） |
| `validators.py` | 未开始 |
| `tts_adapter.py` | 未开始（复用 `tts_cli.py` 的调用方式，改成进程内常驻模型） |
| `rvc_adapter.py` | 未开始（等 Applio 装完确认 CLI 参数） |
| `audio_composer.py` | 未开始（FFmpeg 已可用） |
| `orchestrator.py` | 未开始 |
| `main.py` | 未开始 |

按任务书要求，先跑通单句（阶段四），再设计集成器（阶段五），最后整集导出。
单句的 TTS 那半已经通了，还差 RVC 那半。
