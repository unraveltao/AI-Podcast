# media

两类文件，别混。混了以后没人分得清哪个能发、哪个只是参考。

| 目录 | 放什么 | 命名 |
|---|---|---|
| `voice-samples/` | 有授权的参考声音、候选试听片段 | `角色名-来源.ext`，如 `lin-teacher-own.mp3` |
| `episode-audio/` | 试读、配音成品、发布前音频 | `EP001-试读-v1.mp3`、`EP001-成品.mp3` |
| `voice-models/` | RVC 音色模型（`.pth` + `.index`），**不是音频** | 一模型一目录，说明见 [voice-models/README.md](voice-models/README.md) |

## 注意

- **音频不进 git**（见 `.gitignore`）：体积大、可重新生成。换机器时单独拷这两个目录。
- 存进 `voice-samples/` 之前先确认授权，并把来源和范围记进 [`docs/voice-guide.md`](../docs/voice-guide.md) 的角色档案表。
- `episode-audio/` 里的文件不是资料库，是产物。脚本永远以 `episode.md` 第 5 节为准 —— 音频和稿子不一致时，改音频。
