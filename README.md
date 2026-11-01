# 心理学播客

用少量文件跑通「选题 → 查资料 → 写稿 → 配音 → 复盘」的播客工作区。
不是网站、不是应用，是一套让**人**和**Agent** 都不跑偏的文件夹约定。

**状态**：目录和文档已就位，第一集还是空的。目前零成品。

---

## 先看哪份

| 你想知道 | 打开 |
|---|---|
| 怎么开新一集、每个文件夹放什么 | 本文件，往下看 |
| 一集长什么样、要填哪些栏 | [`templates/episode-template.md`](templates/episode-template.md) |
| 发到哪、怎么变现 | [`docs/platforms.md`](docs/platforms.md) |
| 节目定位、十种情景、科普边界 | [`docs/project-guide.md`](docs/project-guide.md) |
| 声音标签怎么用、怎么选角色音 | [`docs/voice-guide.md`](docs/voice-guide.md) |
| Agent 干活时的规矩 | [`AGENTS.md`](AGENTS.md) |

三份主文档各管一件事：**README 让你读懂、模板让你照着填、platforms 让你知道往哪发**。
另外三份（project-guide / voice-guide / AGENTS）是填模板时才会翻的参考，平时不用看。

---

## 目录

```text
psychology-podcast/
├── README.md                         # 本文件：入口与导航
├── AGENTS.md                         # Agent 工作规则（读取顺序、硬约束）
├── docs/
│   ├── project-guide.md              # 节目定位、五段结构、十种情景、科普边界
│   ├── voice-guide.md                # 声音标签、选音流程、授权
│   └── platforms.md                  # 发布平台与变现路线
├── episodes/
│   ├── index.csv                     # 全集的轻量索引：查重 + 看进度
│   └── EP001-emotion-labeling/
│       └── episode.md                # 这一集的资料、脚本、配音备注、审核记录
├── templates/
│   └── episode-template.md           # 新一集的空白模板
└── media/
    ├── README.md                     # 两类音频各放什么、怎么命名
    ├── voice-samples/                # 有授权的参考声音、候选试听
    └── episode-audio/                # 试读、配音成品、发布前音频
```

一句话记忆：**AGENTS 说怎么干，docs 说节目规则，episodes 放每集内容，templates 拿来复制，media 放声音。**

---

## 怎么开一集

以 EP002 为例，六步：

1. **查重** —— 打开 `episodes/index.csv`，确认 `core_concept` 和 `scenario_id` 没和近五集撞。
2. **建目录** —— `mkdir episodes/EP002-主题英文名`，把模板复制进去：
   ```bash
   cp templates/episode-template.md episodes/EP002-主题英文名/episode.md
   ```
3. **填 front matter** —— `id`、`title`、`core_concept`、`scenario_id`、`scenario_type`、`character_relationship`。这六项是索引和查重的依据，先填对。
4. **写前四节** —— 目标 → 资料核查 → 情景与角色 → 分段大纲。**第 2 节没填完不要动第 5 节**，这是这套结构唯一强制的地方。
5. **写脚本、配音** —— 脚本进第 5 节；音频放 `media/episode-audio/`，第 6 节记下用的是哪个音色、试听了几版。
6. **过审核、更新索引** —— 第 7 节四项都确认后，`status` 改 `approved`，再回 `index.csv` 补这一行。

一集一个文件夹、一个 `episode.md`。**不要提前拆成 brief / research / script 四个文件** —— 等单集真的长到翻不动了再拆，拆早了只会增加同步成本。

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

## 每一格放什么

| 路径 | 放什么 | 什么时候用 |
|---|---|---|
| `AGENTS.md` | 读取顺序、保存位置、审核要求 | 每次叫 Agent 前它先读；保持短小，只放跨任务有效的规则 |
| `docs/project-guide.md` | 节目定位、五段结构、十种情景、轮换、科普边界 | 规划选题、写新稿时读 |
| `docs/voice-guide.md` | 标签含义、试听方法、角色音色 | 选音或调配音表现时读 |
| `docs/platforms.md` | 各平台适合做什么、能怎么变现、发布顺序 | **做完三集再读**，别在选题阶段就按平台反推内容 |
| `episodes/index.csv` | 标题、知识点、情景、状态、平台摘要 | Agent 查重、你看进度 |
| `episodes/EPxxx-.../episode.md` | 这一集的全部内容，七个栏目 | 写和改当前集时读 |
| `templates/episode-template.md` | 空白结构 | 开新集时复制 |
| `media/voice-samples/` | 有授权的参考声音、候选片段 | 选音试听；Agent 只读标签，不加载音频 |
| `media/episode-audio/` | 试读、成品、发布前音频 | 人工试听和导出，不是资料库 |

---

## 三条边界

1. **每集只讲一个主要心理学概念。** 想讲两个，就是两集。
2. **不编造研究、作者、年份、期刊。** 查不到就不写，写成"有一种说法是"也算编造。
3. **不做诊断、不贴标签、不承诺疗效。** 说"这种反应常被叫作反刍"，不说"你是反刍型人格"。

---

## 接下来

1. 把手上那份播客大纲的核心规范搬进 `docs/project-guide.md`（现在那里是候选情景，不是你的原稿）。
2. 把《声音角色选型指南》搬进 `docs/voice-guide.md`。
3. 把第一集「老师与学生」的情景稿放进 `episodes/EP001-emotion-labeling/episode.md` 第 5 节，补齐资料来源和 `voice_tags`。
4. 手动做完一到三集，再回来看哪些栏目真的用不上 —— 那时删，比现在猜准。
