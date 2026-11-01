# media

两类文件，别混。混了以后没人分得清哪个能发、哪个只是参考。

| 目录 | 放什么 | 命名 |
|---|---|---|
| `voice-samples/` | 有授权的参考声音、候选试听片段 | `角色名-来源.ext`，如 `lin-teacher-own.mp3` |
| `episode-audio/` | 试读、配音成品、发布前音频 | `EP001-试读-v1.mp3`、`EP001-成品.mp3` |

**RVC 音色模型（`.pth` + `.index`）已经搬走了**，不在 `content/` 里 ——
它们在实现端的 [`pipeline/engines/rvc-models/`](../../pipeline/engines/rvc-models/)。
模型是"引擎零件"不是"声音素材"，跟引擎放一起才好打包。说明和版权警告在那边的 README。

## 注意

- **音频不进 git**（见 `.gitignore`）：体积大、可重新生成。换机器时单独拷这两个目录。
- 存进 `voice-samples/` 之前先确认授权，并把来源和范围记进 [`docs/voice-guide.md`](../docs/voice-guide.md) 的角色档案表。
- `voice-samples/` 现在**是空的**。没有参考音频，IndexTTS 合成不了 —— 这是整条管线当前唯一的硬阻塞。
- `episode-audio/` 里的文件不是资料库，是产物。脚本永远以 `episode.md` 第 5 节为准 —— 音频和稿子不一致时，改音频。
