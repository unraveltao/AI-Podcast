# Agent 工作规则

开始任何任务前先读本文件。这里只放**跨任务都有效**的规则；某一集具体怎么写，不在这里。

## 先判断：这次动的是哪一边

| 动的是 | 去哪 | 例子 |
|---|---|---|
| 内容 | `content/` | 选题、大纲、脚本、角色听感、发布计划 |
| 声音生产 | `pipeline/` | 引擎、参数、代码、YAML 剧本、产物 |

**稿子改了就只动 `content/`；参数和代码改了就只动 `pipeline/`。**
两边唯一的接口是 `pipeline/scripts/EPxxx.yaml`，格式见 `pipeline/scripts/README.md`。

## 读取顺序

1. 本文件
2. 新建或规划单集 → `content/docs/project-guide.md` → `content/episodes/index.csv` → `content/templates/episode-template.md`
3. 处理声音 → `content/docs/voice-guide.md`（**不要无差别加载音频**，只读标签和档案表）；
   要机器参数 → `pipeline/config/characters.yaml`
4. 处理发布或变现 → `content/docs/platforms.md`
5. 碰引擎或跑管线 → `pipeline/docs/environment-report.md`（先看已知的坑）
6. 改结构或命名 → 先看 `README.md` 的目录表，别自己发明目录

## 内容侧硬规则

- 每集只讲**一个**主要心理学概念。
- 写稿前查 `content/episodes/index.csv`：`core_concept` 不与近五集重复，`scenario_id` 不与上一集相同。
- 情景从 `content/docs/project-guide.md` 第三节选，选完在 front matter 记下 `scenario_id`。
- **不编造研究、作者、年份、期刊。** 查不到就删掉那句话，不写"研究表明"。
- 不给听众或角色下诊断、不贴人格标签、不承诺疗效。
- 草稿只写进 `content/episodes/EPxxx-主题名/episode.md`，不动别人那一集。
- **未经人工确认，不把 `status` 改成 `approved`，不发布。** 最多写到 `review`。
- 一集做完，更新 `content/episodes/index.csv` 对应那一行。

## 实现侧硬规则

- **不修改 IndexTTS 原始代码。** 确实必要时先说明理由、等确认。
- **不升级、降级或覆盖 IndexTTS 的依赖。** 它现在的 torch 2.8.0+cu128 是能跑的状态。
- Applio 用独立 Python 环境，装进 `pipeline/engines/applio`，跟 `rvc-models` 放一起。
- 引擎位置只写在 `pipeline/config/settings.yaml`，不要在代码里硬编码路径。
- **模型推理串行。** 8 GB 显存装不下 TTS 和 RVC 同时在线，不要为了快就并发。
- 失败要能重试，中间文件（`raw/`、`converted/`）保留，方便 A/B 试听。
- 失败时不能覆盖已完成的音频文件。
- 每句一段 = 一次 TTS 调用。不要把整集塞进一次调用。

## 不要做

- 不要为了"结构完整"新建空文件或空目录。
- 不要把整篇脚本复制进 `index.csv`，那里只放摘要。
- 不要改 `content/media/` 里的音频文件（只读，除非明确要求）。
- 不要在 `content/episodes/` 下建共享笔记 —— 共享的东西属于 `content/docs/`。
- 不要顺手"优化"别人的集数措辞，除非被点名。
- 不要用空文件骗过校验（比如造一个假的 `bpe.model`）。宁可报错，不要埋雷。
- 不要为了修 Applio 去动 IndexTTS 的环境。两条线互不干扰。

## 保存与命名

- 单集目录：`content/episodes/EPxxx-英文短名`（如 `EP001-emotion-labeling`），编号三位、不复用。
- 剧本 YAML：`pipeline/scripts/EPxxx.yaml`，跟单集编号一致。
- 成品音频：`content/media/episode-audio/EPxxx-试读-v1.mp3`、`EPxxx-成品.mp3`。
- 管线产物：`pipeline/outputs/EPxxx/{raw,converted,final}/`。
- 声音样本：`content/media/voice-samples/角色名-来源.ext`，授权写进 `content/docs/voice-guide.md` 档案表。
- RVC 模型：`pipeline/engines/rvc-models/一模型一目录/`。

## 已知环境坑（别重复踩）

| 坑 | 表现 | 怎么办 |
|---|---|---|
| 系统没有可用 Python | `python` 是 Store 占位符，`C:\Python312` 不存在 | 用 `E:\Apps\AI\Index_tts2.5\.venv\Scripts\python.exe` |
| 官方 CLI 用不了 | `cli_v2 synth` 报缺 `bpe.model` 直接退出 | 用 `pipeline/tts_cli.py`，别去改 `cli_v2.py` |
| 显存吃紧 | 8 GB，桌面已占 2 GB；WebUI 开着时合成慢 **70 倍** | 跑批前关掉 7860 上的 WebUI 和浏览器 |
| 参考音频不全 | `doctor` / `student` 的 `reference_audio` 还是 null | 各补一段 5–15 秒干净人声；`narrator` 已有 |
| 素材格式不一 | mp3 / m4a / 40k wav 混着来 | 一律先过 `pipeline/audio_prep.py` |
| GitHub 推送 | 走 https 报 `CONNECT tunnel failed, response 502`，`gh` 网页登录也失败（github.com 主站被阻断） | **用 SSH**：`origin` 已是 `git@github.com:unraveltao/AI-Podcast.git`，`git push` 直接可用。新建仓库只能在网页手动建，连接器令牌没有建仓权限（403） |

细节见 `pipeline/docs/environment-report.md`。
