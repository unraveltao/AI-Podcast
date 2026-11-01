# 环境检查报告

**检查时间**：2026-11-01 18:16 – 18:30（GMT+8）
**检查方式**：只读探测；两处环境缺陷已按授权修复，修复内容见第五节。
**对应阶段**：任务书「阶段一：环境检查」

---

## 一、结论

**阶段一通过，可以进入阶段二（安装 Applio），但有三个前提要先处理：**

1. 参考音频是空的 —— IndexTTS 没有 `--voice` 就无法合成，单句测试做不了。
2. CLI 路线被 IndexTTS 自己的校验器挡住（详见第四节），需要改用直接 import。
3. 显存只有 8 GB，且已被桌面占 2.1 GB；IndexTTS 与 Applio 必须串行，不能同时加载。

---

## 二、环境快照

| 项 | 实测值 | 判定 |
|---|---|---|
| 操作系统 | Windows 11 家庭版，Build 26200 | 通过 |
| 内存 | 15.8 GB | 通过 |
| 显卡 | NVIDIA GeForce RTX 4060 Laptop GPU，8188 MiB | 通过 |
| 显卡驱动 | 596.49（支持的最高 CUDA 运行时 13.2） | 通过 |
| 显存占用（检查时） | 2131 MiB / 8188 MiB，被桌面进程占用（GenOffice、CrossDeviceResume） | 留意 |
| PyTorch（IndexTTS 环境内） | 2.8.0+cu128，`torch.cuda.is_available() = True` | 通过 |
| CUDA（torch 自带） | 12.8 | 通过 |
| IndexTTS 版本/位置 | IndexTTS-2.5，`E:\Apps\AI\Index_tts2.5` | 通过 |
| IndexTTS Python | `.venv` 3.11.13（`.python-version` = 3.11.13，uv 管理） | 通过 |
| IndexTTS 启动方式 | `start_webui.bat` → `webui.py --fp16 --host 127.0.0.1 --port 7860` | 通过 |
| IndexTTS 服务状态 | 检查时 7860 端口**正在运行**（`/gradio_api/info` 返回 200） | 占用中 |
| 是否已产出 WAV | `outputs/` 下 15 个 `spk_*.wav`，最新 2026-11-01 01:29 | **已验证可用** |
| 模型权重 | `checkpoints/` 齐全：`gpt.pth` 3.26 GB、`s2mel.pth` 415 MB、`codec.pth` 607 MB、`qwen0.6bemo4-merge`、`hf_cache/` | 通过 |
| 参考音频目录 | `E:\Apps\AI\Index_tts2.5\prompts\` **为空** | **阻塞项** |
| 自带示例音频 | `examples/voice_01.wav` … `voice_12.wav` 共 12 段，可临时当 `--voice` 用 | 可用 |
| 系统 Python | `py -0p` 列出 `C:\Python312`，**该目录不存在**（注册表残留）；`python` 是 Microsoft Store 占位符 | **不可用** |
| 可用解释器 | uv 的 3.11.18（`AppData\Roaming\uv\python\`）、IndexTTS venv 3.11.13。**没有 3.13** | 通过 |
| Git | 2.55.0.windows.3 | 通过 |
| FFmpeg | 9.0.2-full_build（Gyan 构建，带 libx264/libmp3lame/libvorbis） | **已修复** |
| Applio | D:/E: 盘 4 层内无任何 applio 目录 | 未安装 |
| RVC 模型 | `pipeline/engines/rvc-models/{yelan,ganyu}`，v2 / 40k / f0=1，`.pth` 与 `.index` 配套 | 通过 |
| 磁盘 | C: 216 GB 空闲 / D: 398.7 GB / E: 1.7 TB | 通过 |

---

## 三、必须知道的三件事

### 3.1 系统级 Python 事实上不存在

`py -0p` 会告诉你 `C:\Python312` 在，但那个目录是空的 —— 注册表残留。`python.exe`
指向 `WindowsApps` 下的 Microsoft Store 占位符，运行它会弹商店。

**影响**：任何脚本都不能写 `python main.py` 就完事。要么在 venv 里跑，要么用绝对路径
指定解释器。`pipeline/config/settings.yaml` 里所有 Python 路径都写死了绝对路径，就是为了这个。

### 3.2 FFmpeg 原来装了但调不动

winget 装的是 Gyan 版 9.0.2，本体在
`%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_...\ffmpeg-9.0.2-full_build\bin\`，
但 `WinGet\Links\` 下的 `ffmpeg.exe` / `ffplay.exe` / `ffprobe.exe` 三个转发文件都是 **0 字节**，
调用时直接报"不是有效的应用程序"。已修复，见第五节。

### 3.3 IndexTTS 的 CLI 在 2.5 上跑不起来

`python -m indextts.cli_v2` 提供 `synth / batch / concat / check` 子命令，看着正是我们要的，
但 `cli_v2.py` 的 `REQUIRED_MODEL_FILES` 里还留着 `bpe.model`（IndexTTS-2.0 时代的分词表）。
2.5 已改用 tiktoken（`checkpoints/multilingual_zh_ja_yue_char_del.tiktoken`），
`infer_v2_5.py` 全程不读 `bpe.model`，整个安装里也没有这个文件。

实测结果：

```
$ python -m indextts.cli_v2 synth --text "测试" --voice examples/voice_01.wav --output probe.wav
ERROR: missing required model files: bpe.model
```

`_run_synth`（`cli_v2.py:554`）在加载模型**之前**就调 `_report_missing_model_resources()`，
所以不是"跑了但效果差"，而是**一步都没开始就退出**。`_run_batch`（`cli_v2.py:622`）同样如此。

**判断**：这是上游校验器没跟上 2.5 的遗留问题，不是本机装坏了 —— 同一套 checkpoints
在 WebUI 里已经成功出过 15 段音频。

**为什么不直接改 cli_v2**：改一处不够。`_load_indextts2()` 导入的是 2.0 的类
（`infer_v2.IndexTTS2`），它构造时要读 `bpe_model`；2.0 的类收 `use_fp16`、2.5 收 `use_bf16`；
2.5 的 `infer()` 还多一个必填的 `lang` 参数。三处全对不上，改它等于替上游维护一个分叉，
他们一升级就全废。而且违反开发原则第 2 条。

**处置：自己写一层薄封装**，`pipeline/tts_cli.py`。逻辑只有「解析参数 → 调 `IndexTTS2` → 落盘」，
不碰 IndexTTS 一行代码，将来的 `tts_adapter` 直接复用它。

```bash
E:\Apps\AI\Index_tts2.5\.venv\Scripts\python.exe pipeline/tts_cli.py \
    --text "今天我们来聊一聊焦虑。" \
    --voice content/media/voice-samples/narrator-selfrecorded.wav \
    --output pipeline/outputs/_smoke/raw_test_short.wav
```

**实测结果（2026-11-01 18:45）**：

| 项 | 数值 |
|---|---|
| 模型加载 | 19.7 s |
| 11 字 → 3.87 s 音频 | 合成 8.5 s，RTF **2.2** |
| 输出规格 | 22050 Hz / 单声道 / pcm_s16le |

**结论：CLI 路线已通。** 代价是绑定 `indextts.infer_v2_5` 这个内部 API，上游改签名时会断 —— 但断的时候好查。

---

## 四、显存与并发

| 项 | 数值 |
|---|---|
| 总显存 | 8188 MiB |
| 检查时已占用 | 2131 MiB（桌面进程） |
| IndexTTS 权重占用 | 约 3.2 GB（`gpt.pth` 单文件 3.26 GB） |
| Applio RVC 推理需求 | 约 2–4 GB |

三者相加已经贴到 8 GB 上限。所以：

- **IndexTTS WebUI 常驻时会抢显存。** 跑批处理前先关掉 7860 上的 WebUI。
- **TTS 与 RVC 必须串行**，不能同时加载。任务书第 8 条原则本来就是这么定的，现在是硬约束。
- 批量合成时让 IndexTTS 常驻、RVC 逐段调起，是显存最省的顺序。

**这不是理论推测，是实测出来的**：同一段 12 秒音频，WebUI 在跑时合成花了 351 秒（RTF 25.6，
`s2mel` 每步 7.2 秒）；停掉 WebUI 后，11 字合成只要 8.5 秒（RTF 2.2，每步 0.1 秒）。**差 70 倍**，
原因就是显存不够、WDDM 把权重换到共享内存了。

推论：**长集渲染前，把浏览器、微信、QQ 这类吃显存的程序也关掉**，比换显卡便宜。

---

## 五、本次修改了什么

两处，都属于"配置有误、按授权修复"，**没有动 IndexTTS 源码、没有动依赖版本**。

### 5.1 修复 FFmpeg 转发文件（已改）

```powershell
# 删除 3 个 0 字节转发文件，改成指向真实二进制的硬链接（同盘、免管理员）
Remove-Item "$env:LOCALAPPDATA\Microsoft\WinGet\Links\ffmpeg.exe"
New-Item -ItemType HardLink -Path "...\Links\ffmpeg.exe" -Target "...\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
```

`ffplay` / `ffprobe` 同样处理。验证：

```
$ ffmpeg -version
ffmpeg version 9.0.2-full_build-www.gyan.dev
$ ffprobe -version
ffprobe version 9.0.2-full_build-www.gyan.dev
```

用的是硬链接不是复制，所以没有多占 680 MB。副作用：以后 `winget upgrade` 换版本时，
这三个硬链接会指向旧文件，需要重做一次（或者把真实 bin 目录加进 PATH 后删掉它们）。

### 5.2 把 IndexTTS CLI 的模型目录指向本地（已改）

CLI 默认去 `C:\Users\iron tom\AppData\Local\IndexTTS\models\IndexTTS-2` 找权重，那里是空的。
已写入用户级配置：

```
$ python -m indextts.cli_v2 config set model_dir "E:\Apps\AI\Index_tts2.5\checkpoints"
model_dir = E:\Apps\AI\Index_tts2.5\checkpoints
```

配置存在 `%LOCALAPPDATA%\IndexTTS\`，不在 IndexTTS 目录内，也不影响 `webui.py`
（它的默认值是 `./checkpoints`，本来就走本地）。`bpe.model` 的误报仍在，属于上游问题，未绕。

### 5.3 目录重构（已改）

按"资源端 / 实现端"拆开，细节见仓库根 `README.md`。

---

## 六、没做的事，以及为什么

| 没做 | 原因 |
|---|---|
| 装 Applio | 任务书要求环境检查确认后再装；现在 TTS 已通，可以装了，等你点头 |
| 改 `cli_v2.py` 本身 | 改一处不够（导入、构造参数、infer 签名三处都不兼容），等于替上游养分叉。改用自写封装绕开 |
| 补 doctor / student 的参考音频 | 那是**你的**声音素材，用谁的声音、有没有授权，我不能替你决定。narrator 已用你给的录音补上 |
| 创建 `bpe.model` 假文件骗过校验 | 会让"看起来能跑"掩盖真问题，属于埋雷，不做 |
| 升级/降级任何 Python 依赖 | 原则第 7 条，且当前 torch 2.8.0+cu128 已验证可用 |
| 修 `py -0p` 的注册表残留 | 它不影响任何实际运行，改注册表风险大于收益。已通过配置写死绝对路径规避 |
| 试听合成结果 | 我听不了音频。**这一项需要你亲耳判断**，文件在 `pipeline/outputs/_smoke/` |

---

## 七、下一步

**阶段四的单句 TTS 已经完成**（2026-11-01 18:45）：

```
content/media/voice-samples/narrator-selfrecorded.wav   ← 你的录音，已归一化
        ↓  IndexTTS 2.5（pipeline/tts_cli.py）
pipeline/outputs/_smoke/raw_test.wav         12.09 s   长句（自动切两段）
pipeline/outputs/_smoke/raw_test_short.wav    3.87 s   短句
```

下一步是**阶段二：安装 Applio**，装到 `pipeline/engines/applio`（跟 `rvc-models` 放一起，方便打包）。

装完之后要立刻验证的三件事：自带 Python 版本、有没有 CLI 入口、能不能用绝对路径指定模型。
摸清楚这些才写 `rvc_adapter`。

⚠️ 注意：为做对照测试，**7860 上的 IndexTTS WebUI 已被我停掉**（PID 8528）。
要重新打开就双击 `E:\Apps\AI\Index_tts2.5\start_webui.bat`。
但跑管线时别开它 —— 实测会让合成慢 70 倍。

---

## 八、阶段二：Applio 安装结果（2026-11-01 19:43）

### 8.1 装了什么

| 项 | 值 |
|---|---|
| 版本 | **Applio V3.7.1**（官方 Compiled Windows 包，最新） |
| 来源 | `huggingface.co/IAHispano/Applio` → `Compiled/Windows/ApplioV3.7.1.zip` |
| 大小 | 6,777,319,254 字节（6.31 GiB），校验一致 |
| 位置 | `pipeline/engines/applio/`（跟 `rvc-models` 同级，便于打包） |
| Python | 自带 `env/python.exe` = **3.12.15** |
| PyTorch | **2.11.0+cu128**，`cuda_available = True` |
| FFmpeg | 自带 `ffmpeg.exe` / `ffprobe.exe`（52 MB / 122 MB） |

下载过程有波折：第一次用镜像下载在 82 MB 处被服务器掐断（`schannel: server closed abruptly`），
改成 `curl -C -` 断点续传循环重试后，一次跑到 6.31 GiB 完成。

### 8.2 三个关键结论

**① 环境完全隔离。** Python 3.12.15 / torch 2.11.0，跟 IndexTTS 的 3.11.13 / torch 2.8.0
互不干扰。符合开发原则第 3、7 条 —— 装 Applio 没有动 IndexTTS 一个字节。

**② 有 Python API，不用模拟点 Gradio。** `core.py` 提供：

```python
core.run_infer_script(
    pitch, index_rate, volume_envelope, protect, f0_method,
    input_path, output_path, pth_path, index_path,
    f0_autotune, f0_autotune_strength, proposed_pitch, proposed_pitch_threshold,
    export_format, embedder_model, ...
)
```

这直接满足任务书 7.2 的「优先使用官方 CLI，而不是模拟点击 Gradio 页面」。

**③ 模型验证通过。** `core.run_model_information_script()` 读两个 `.pth` 都正常返回：

```
Sampling Rate: 40k    Max Speakers ID: 0
```

采样率 40k 跟 `rvc-models/README.md` 里记的一致；单说话人；能读出架构参数说明是
**推理权重而不是训练检查点**。元数据（作者、epoch）为 None，是分发模型被剥离元数据的正常现象。

### 8.3 依赖齐全，首次推理不用联网

| 需要的东西 | 是否随包 |
|---|---|
| `rvc/models/predictors/rmvpe.pt`（f0 提取） | ✅ |
| `rvc/models/predictors/fcpe.pt` | ✅ |
| `rvc/models/embedders/contentvec/`（声学特征） | ✅ |

三个 f0 方法（rmvpe / fcpe / swift）都能直接用。

### 8.4 模型不用搬

Applio 没有强制的 `assets/weights/` 目录，`.pth` 和 `.index` 都靠参数传绝对路径。
所以 `pipeline/engines/rvc-models/` 保持唯一存放点，不用往 Applio 里复制副本。

### 8.5 下一步

阶段二、三已完成。剩下**阶段四的后半：真跑一次 RVC 转换** ——
把 `raw_test_short.wav` 过一遍 yelan 模型，对比转换前后。
这一步会同时验证显存、参数和音色，跑完就能进阶段五写集成器。

