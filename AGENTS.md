# Agent 工作规则

开始任何任务前先读本文件。这里只放**跨任务都有效**的规则；某一集具体怎么写，不在这里。

## 读取顺序

1. 本文件
2. 新建或规划单集 → `docs/project-guide.md` → `episodes/index.csv` → `templates/episode-template.md`
3. 处理声音 → `docs/voice-guide.md`（**不要无差别加载 `media/` 里的音频**，只读标签和档案表）
4. 处理发布或变现 → `docs/platforms.md`
5. 改结构或命名 → 先看 `README.md` 的目录表，别自己发明目录

## 硬规则

- 每集只讲**一个**主要心理学概念。
- 写稿前查 `episodes/index.csv`：`core_concept` 不与近五集重复，`scenario_id` 不与上一集相同。
- 情景从 `docs/project-guide.md` 第三节选，选完在 front matter 记下 `scenario_id`。
- **不编造研究、作者、年份、期刊。** 查不到就删掉那句话，不写"研究表明"。
- 不给听众或角色下诊断、不贴人格标签、不承诺疗效。
- 草稿只写进 `episodes/EPxxx-主题名/episode.md`，不动别人那一集。
- **未经人工确认，不把 `status` 改成 `approved`，不发布。** 最多写到 `review`。
- 一集做完，更新 `episodes/index.csv` 对应那一行。

## 不要做

- 不要为了"结构完整"新建空文件或空目录，现在的树够了。
- 不要把整篇脚本复制进 `index.csv`，那里只放摘要。
- 不要改 `media/` 里的音频文件（只读，除非明确要求）。
- 不要在 `episodes/` 下建共享笔记 —— 共享的东西属于 `docs/`。
- 不要顺手"优化"别人的集数措辞，除非被点名。

## 保存与命名

- 单集目录：`EPxxx-英文短名`（如 `EP001-emotion-labeling`），编号三位、不复用。
- 音频：`EPxxx-试读-v1.mp3`、`EPxxx-成品.mp3`，放 `media/episode-audio/`。
- 声音样本：`角色名-来源.ext`，授权情况写进 `docs/voice-guide.md` 档案表。
