# engines

「换台机器也要跟着走」的东西都放这里，方便整个实现端打包带走。

| 目录 | 内容 | 状态 | 进 git |
|---|---|---|---|
| `applio/` | Applio V3.7.1 编译包 + 自带 Python 3.12.15 + 自带 ffmpeg | **已安装** | 否 |
| `rvc-models/` | RVC 音色模型 `.pth` + `.index` | 已就位 | 否（二进制 + 版权） |

## 不在这个目录里的引擎

**IndexTTS 2.5** 留在 `E:\Apps\AI\Index_tts2.5`，不搬也不复制 —— 它有 4 GB 权重和独立
venv，搬动只会带来路径错误。位置记在 `pipeline/config/settings.yaml` 的 `engines.indextts`。

要打包成完全自包含的安装包时，才需要把它也收进 `engines/`，并改 `settings.yaml` 一处。

## rvc-models 的两个音色

`yelan` 和 `ganyu` 是《原神》角色的 RVC 模型，**只能做内部样片，不能商用**。
理由（IP 归属、声音人格权、《人工智能生成合成内容标识办法》）写在
[`rvc-models/README.md`](rvc-models/README.md) 第二节，动之前先看。

两个模型都是 v2 架构、40 kHz 训练、带 f0。转换时采样率必须跟 40 kHz 对齐，
写 48 kHz 会重采样，声音会发闷。

## applio 装好之后的三个结论

**1. 自带环境，不用碰 IndexTTS。**
`env/python.exe` = Python 3.12.15，torch 2.11.0+cu128，CUDA 可用。跟 IndexTTS 的
3.11.13 / torch 2.8.0 完全隔离，符合开发原则第 3、7 条。

**2. 有现成的 Python API，不用模拟点界面。**
`core.py` 里 `run_infer_script(...)` 直接收全部参数：

```python
run_infer_script(
    pitch=0, index_rate=0.6, volume_envelope=1.0, protect=0.33,
    f0_method="rmvpe", input_path=..., output_path=...,
    pth_path=..., index_path=...,
    f0_autotune=False, f0_autotune_strength=0.0,
    proposed_pitch=False, proposed_pitch_threshold=0.0,
    export_format="WAV", embedder_model="contentvec",
)
```

这比点 Gradio 稳得多，`rvc_adapter` 就调它。

**3. 模型用绝对路径，不用搬文件。**
包里没有 `assets/weights/` 这种强制目录，`.pth` / `.index` 都靠参数传。
所以 `rvc-models/` 保持唯一存放点，不用往 Applio 里复制。

**4. 依赖全随包，首次推理不用联网。**
`rvc/models/predictors/rmvpe.pt`、`fcpe.pt`、`rvc/models/embedders/contentvec/` 都在。

**5. 模型验证通过。**
`core.run_model_information_script()` 读 `yelan.pth` / `ys_ganyu.pth` 均正常返回，
`Sampling Rate: 40k`、单说话人。说明是推理权重，不是训练检查点。

## 怎么启动界面（偶尔手动试听用）

```powershell
cd pipeline/engines/applio
.\run-applio.bat        # 等价于 env\python.exe app.py --open
```

**跑管线时别开它** —— 跟 IndexTTS WebUI 一样会抢显存。
