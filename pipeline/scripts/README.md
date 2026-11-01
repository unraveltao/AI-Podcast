# 剧本 YAML 格式（交给 ChatGPT 照着写）

这个目录放**每集一份的剧本 YAML**。写的人不是 Agent，是 ChatGPT —— 所以这份说明必须
自给自足：把下面整段连同示例一起贴给它，它就能产出能直接跑的稿子。

程序（`pipeline/orchestrator.py`）只认这里定义的字段。**多余字段会被忽略，缺字段会报错。**

---

## 一、文件名与位置

```
pipeline/scripts/EP001.yaml          ← 一集一个文件
pipeline/scripts/EP002.yaml
```

- 文件名 = `EP` + 三位编号，跟 `content/episodes/` 里的目录编号一致。
- 一个文件只写一集。不要往同一个文件里塞两集。
- 编码必须是 **UTF-8（不带 BOM）**。带 BOM 会导致第一个字段读不出来。

---

## 二、完整示例

```yaml
episode:
  id: "EP001"
  title: "我现在到底是什么感受？"
  source: "content/episodes/EP001-emotion-labeling/episode.md"   # 可选，仅供追溯

segments:
  - id: "001"
    speaker: "doctor"
    text: "你好，欢迎来到今天的心理学播客。"
    pause_after_ms: 700

  - id: "002"
    speaker: "student"
    text: "老师，我最近总觉得说不上来哪里不对。"
    pause_after_ms: 500

  - id: "003"
    speaker: "doctor"
    text: "那我们先不急着给它起名字。"
    pause_after_ms: 1000
```

---

## 三、字段说明

### `episode`

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | `EP001` 这种格式，三位数字，不复用 |
| `title` | 是 | 这一集的标题，会写进文件名和日志 |
| `source` | 否 | 稿子来源路径，只用于追溯，程序不读它 |

### `segments[]`

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `id` | 是 | 字符串 | 段内唯一，三位数字。**决定拼接顺序，不是数组顺序** |
| `speaker` | 是 | 字符串 | 必须能在 `config/characters.yaml` 里找到同名 key |
| `text` | 是 | 字符串 | 要合成的话。**一段 = 一次 TTS 调用**，别写太长 |
| `pause_after_ms` | 否 | 整数 | 这段之后的静音，默认取 `settings.yaml` 的 700 |
| `emotion_text` | 否 | 字符串 | 传给 IndexTTS 的情绪描述，如"疲惫、压低声音" |
| `emotion_weight` | 否 | 0–1 小数 | 情绪强度，默认 0.8 |

---

## 四、写稿时必须遵守的六条

1. **`speaker` 必须是 `characters.yaml` 里已有的 key。** 想加新角色，先改 `characters.yaml`，
   不要在 YAML 里现编名字。
2. **一段 8–40 个汉字。** 太短会被切碎、语气断裂；太长 IndexTTS 容易吞字、情绪漂移。
   一段念完大约 3–12 秒。
3. **不要在 `text` 里写舞台提示。** `（停顿）`、`[叹气]`、`*笑声*` 都会被当正文念出来。
   停顿用 `pause_after_ms`，情绪用 `emotion_text`。
4. **标点要全，但只用中文标点。** 句号、逗号、问号、省略号都给全 —— TTS 靠标点断句。
   不要用 `...`，用 `……`。
5. **数字和英文缩写写成能直接念的形式。** 写"三点五"，不写"3.5"；写"焦虑症"，不写"GAD"。
6. **`id` 从 001 连续编号，不要跳号、不要重复。** 跳号会让续跑时对不上已完成的段落。

---

## 五、程序会检查什么

运行前会做这些校验，任何一条不过就直接报错、不开始合成：

- 文件存在、UTF-8 可解析
- `episode.id` 格式是 `EP` + 三位数字
- `segments` 非空
- 每段 `id` 唯一、`text` 非空
- 每个 `speaker` 都在 `characters.yaml` 里
- 每个 speaker 的 `reference_audio` 已填且文件存在
- RVC 模型的 `.pth` 和 `.index` 都存在

最后两条现在会失败 —— 参考音频还没补（见 `config/characters.yaml` 顶部说明）。

---

## 六、产出位置

```
pipeline/outputs/EP001/
├── raw/          EP001-001-raw.wav         TTS 原始音，没换声
├── converted/    EP001-001-converted.wav   换声后
└── final/        EP001.wav / EP001.mp3     拼好的整集
```

中间文件默认保留，方便 A/B 试听。`settings.yaml` 里 `runtime.keep_intermediate` 控制。
