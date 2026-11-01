# 心理学播客

一个仓库，两件事：**写节目** 和 **把节目变成声音**。

**状态**：资源端已就位，实现端刚做完环境检查。目前零成品音频。

---

## 两边是什么

| 端 | 目录 | 管什么 | 谁在动它 |
|---|---|---|---|
| **资源端** | `content/` | 选题、大纲、脚本、声音素材、发布计划 | 人 + ChatGPT（写稿） |
| **实现端** | `pipeline/` | 把剧本 YAML 变成 WAV / MP3 的代码与引擎 | Agent |

分界只有一条：**`content/` 里放"内容"，`pipeline/` 里放"把内容变成音频的东西"。**
稿子改了只动 `content/`；参数、引擎、代码改了只动 `pipeline/`。两边靠剧本 YAML 交接。

---

## 目录

```text
psychology-podcast/
├── README.md                      # 本文件：入口与导航
├── AGENTS.md                      # Agent 工作规则（两侧边界 + 硬约束）
│
├── content/                       # ── 资源端 ──────────────────────
│   ├── docs/
│   │   ├── project-guide.md       # 节目定位、五段结构、十种情景、科普边界
│   │   ├── voice-guide.md         # 声音标签、选音流程、授权
│   │   └── platforms.md           # 发布平台与变现路线
│   ├── episodes/
│   │   ├── index.csv              # 全集的轻量索引：查重 + 看进度
│   │   └── EP001-emotion-labeling/
│   │       └── episode.md         # 这一集的资料、脚本、配音备注、审核记录
│   ├── templates/
│   │   └── episode-template.md    # 新一集的空白模板
│   └── media/
│       ├── voice-samples/         # 有授权的参考声音（IndexTTS 的 --voice）
│       └── episode-audio/         # 试读、成品、发布前音频
│
└── pipeline/                      # ── 实现端 ──────────────────────
    ├── main.py                    # 入口（待写）
    ├── config/
    │   ├── settings.yaml          # 引擎路径、音频参数、重试策略
    │   └── characters.yaml        # 角色 → 参考音频 / RVC 模型 / 参数
    ├── scripts/                   # 每集剧本 YAML（ChatGPT 写，格式见该目录 README）
    ├── engines/
    │   ├── rvc-models/            # RVC 音色模型（.pth + .index）
    │   └── applio/                # Applio 本体（待安装）
    ├── outputs/                   # raw / converted / final
    ├── logs/
    ├── tests/
    └── docs/environment-report.md # 阶段一产出：环境检查报告
```

一句话记忆：**content 写内容，pipeline 出声，YAML 是两者的接口。**

---

## 先看哪份

| 你想知道 | 打开 |
|---|---|
| 怎么开新一集、每个文件夹放什么 | 本文件，往下看 |
| 一集长什么样、要填哪些栏 | [`content/templates/episode-template.md`](content/templates/episode-template.md) |
| 节目定位、十种情景、科普边界 | [`content/docs/project-guide.md`](content/docs/project-guide.md) |
| 声音标签怎么用、怎么选角色音 | [`content/docs/voice-guide.md`](content/docs/voice-guide.md) |
| 发到哪、怎么变现 | [`content/docs/platforms.md`](content/docs/platforms.md) |
| 剧本 YAML 怎么写（给 ChatGPT） | [`pipeline/scripts/README.md`](pipeline/scripts/README.md) |
| 引擎装在哪、环境有什么坑 | [`pipeline/docs/environment-report.md`](pipeline/docs/environment-report.md) |
| Agent 干活时的规矩 | [`AGENTS.md`](AGENTS.md) |

---

## 怎么开一集

### 内容部分（资源端）

1. **查重** —— 打开 `content/episodes/index.csv`，确认 `core_concept` 和 `scenario_id` 没和近五集撞。
2. **建目录** —— `mkdir content/episodes/EP002-主题英文名`，把模板复制进去：
   ```bash
   cp content/templates/episode-template.md content/episodes/EP002-主题英文名/episode.md
   ```
3. **填 front matter** —— `id`、`title`、`core_concept`、`scenario_id`、`scenario_type`、
   `character_relationship`。这六项是索引和查重的依据，先填对。
4. **写前四节** —— 目标 → 资料核查 → 情景与角色 → 分段大纲。**第 2 节没填完不要动第 5 节。**
5. **写脚本** —— 进第 5 节。这是唯一的原稿，音频永远以它为准。

### 声音部分（实现端）

6. **转 YAML** —— 让 ChatGPT 按 [`pipeline/scripts/README.md`](pipeline/scripts/README.md) 的格式，
   把第 5 节脚本转成 `pipeline/scripts/EP002.yaml`。
7. **跑管线** —— `python pipeline/main.py --script pipeline/scripts/EP002.yaml`（尚未实现）。
8. **试听** —— 成品进 `content/media/episode-audio/`，命名 `EP002-成品.mp3`。
9. **过审核、更新索引** —— 第 7 节四项都确认后，`status` 改 `approved`，再回 `index.csv` 补这一行。

一集一个文件夹、一个 `episode.md`。**不要提前拆成 brief / research / script 四个文件** ——
等单集真的长到翻不动了再拆。

---

## 状态怎么走

`index.csv` 的 `status` 只用五个词，别自创：

| 状态 | 含义 |
|---|---|
| `idea` | 只有选题，还没动笔 |
| `draft` | 脚本在写，资料可能还没核完 |
| `review` | 稿子写完了，等人核心理知识和重复度 |
| `approved` | 人确认过，可以配音 |
| `produced` | 音频出来了，可以发 |

`approved` 只能由人改。Agent 写到 `review` 就停。

---

## 三条边界

1. **每集只讲一个主要心理学概念。** 想讲两个，就是两集。
2. **不编造研究、作者、年份、期刊。** 查不到就不写，写成"有一种说法是"也算编造。
3. **不做诊断、不贴标签、不承诺疗效。** 说"这种反应常被叫作反刍"，不说"你是反刍型人格"。

---

## 接下来

1. **补参考音频** —— `content/media/voice-samples/` 现在是空的，没有它 IndexTTS 合成不了。
2. **装 Applio** —— 阶段二，装到 `pipeline/engines/applio`。
3. **跑通单句** —— IndexTTS 出一段 → RVC 换声 → A/B 试听。
4. 单句通了，再写集成器（阶段五）。

环境检查的完整结论见 [`pipeline/docs/environment-report.md`](pipeline/docs/environment-report.md)。
