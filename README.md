# Dario Genesis — English Dub & English Subtitles

**《达里奥创世录》英文配音 / 英文字幕派生版** · a *derivative work*, not an original film

## 来源与致敬 / Origin & Tribute

**中文**

> 本项目的全部画面、音乐、原始旁白文稿与视觉设计，均出自 **@你好与那啥** 的《达里奥创世录》，
> 其完整源码公开于 **https://github.com/null0526/dario-genesis**。
> 本项目是对该作品的**致敬之作**：我们只做了一件很窄的事——把它翻译成英文、配上一版英文声音、
> 重混音轨、加上英文字幕和一行译者署名。除此之外，我们没有改动原片的任何一帧画面、
> 没有改动原音轨的任何内容、也没有修改原作者的任何一行代码。
> 原作部分的一切版权与署名权，完全归于原作者。

**English**

> Everything you see and hear in the visuals, the music, the original narration script and the visual design
> comes from **_达里奥创世录_ (Dario Genesis) by [@你好与那啥](https://www.bilibili.com/video/BV1mEnb6LEnC)**,
> whose full source code is published at **https://github.com/null0526/dario-genesis**.
> This project is a **tribute**: a narrow, additive layer consisting of an English translation, an English
> voice track, a re-mix, burned-in English subtitles and one credit line on the title card.
> We changed **no frame** of the original picture, **no content** of the original audio, and **no line of the
> author's code**. All rights and attribution for the original work remain entirely with the original author.

## 这是什么 / What this is

一部 11 分 43 秒的 B 站中文科普短片《达里奥创世录》的**英文配音 + 英文字幕版**。

| 项 | 内容 |
|---|---|
| 原作 | 《达里奥创世录》(Dario Genesis)，B 站 UP 主 **@你好与那啥** |
| 原视频 | https://www.bilibili.com/video/BV1mEnb6LEnC （BV1mEnb6LEnC） |
| 原作者源码仓库 | https://github.com/null0526/dario-genesis |
| 原作形式 | WebGL / Canvas + Python **纯代码生成**短片（画面与声音全代码合成，无采样素材） |
| 原片时长 | 703.928 s（11:43.93），五章 |
| 本仓库性质 | **派生作品（derivative work）**：英译 + 英文配音 + 英文字幕 |
| 本仓库不含 | 任何 mp4（视频只放在 [Releases](https://github.com/ZiOstudio/dario-genesis-en/releases)），任何上游代码 |

本仓库做的事情只有一件：把原作者已经发布的成品视频，翻译、配音、重混音轨、烧上英文字幕，再在片头标题卡上追加一行译者署名。画面、音乐、原始中文旁白文稿、视觉设计，全部属于原作者。

> `Not endorsed by Anthropic.` 本项目与 Anthropic 无关，未获其认可或授权。

## 我做了什么 / What I added

全部贡献可以用九项说清（详细参数见下文「技术参数」）：

| # | 贡献 | 具体内容 |
|---|---|---|
| C1 | 全文英译 | 2535 字中文旁白 → 1501 词英文，按语义切分为 53 段，与原文 53 段一一对应 |
| C2 | 英文配音 | 53 段神经网络 TTS，闭环求解每段语速使其贴合原段时长，0 段失败 |
| C3 | 时间轴标定 | 实测母版与上游数据文件之间 **+3.04 s** 的整体偏移，重建全局时基 |
| C4 | 整轨重混 | 人声铺回母版时间轴，与伴奏床按固定增益合成（不做 ducking），至 −15.5 LUFS |
| C5 | 片尾补接 | 定位母版中的真数字静音段，无损截取片尾 22.3 s（含配乐）接回混音轨 |
| C6 | 英文硬字幕 | 327 条 SRT，逐条对齐到字级时间码，烧录进画面 |
| C7 | 片头署名 | 在原标题卡上追加第四块：中英双语译者署名，字号/字距/颜色逐行对齐原卡 |
| C8 | 工程工具 | 12 个 Python 脚本（时基标定、切分、字幕生成、TTS 闭环、混音、署名卡、压制） |
| C9 | 双版本交付 | 硬字幕版（可直接发布）＋ 软字幕版（`-c:v copy` 无损视频流，便于再编辑） |

**没有做**的事（避免误解）：没有重新渲染，没有改动原作者的任何一行代码，没有运行上游 `镜头/` 下的合成工程，没有改动原片画面中的任何一帧像素（除片头卡片上新增的一行署名），没有改动原音轨的内容与结构，没有做人声分离（原作音轨本身不含旁白，天然是 M&E）。完整清单见 [NOTICE.md](NOTICE.md)。

## 下载 / Download

视频不进 git 历史（单文件即数百 MB），只作为 Release 资产提供：

**➡️ [Releases · v1.0.0 — English dub & English subtitles](https://github.com/ZiOstudio/dario-genesis-en/releases/tag/v1.0.0)**

| 文件 | 大小 | 视频 | 字幕 | 片头署名 | 用途 |
|---|---|---|---|---|---|
| `dario-genesis-en-1080p.mp4` | 701,647,596 B（669.1 MiB） | libx264 重编码 | **烧录进画面**（硬字幕） | **有** | **主发布版**，可直接上传平台 |
| `dario-genesis-en-1080p-softsub.mp4` | 778,792,812 B（742.7 MiB） | **`-c:v copy` 无损** | mov_text 软字幕轨 | **无** | 便于再编辑 / 换字幕 |

两种字幕形式在物理上互斥：硬字幕需要重编码视频，软字幕要求视频流不重编码。因此交付两个文件，而不是一个。软字幕版没有片头署名——视频流未重编码，无法叠加。

## 字幕与脚本 / Subtitles & Tools

**字幕（可直接复用）**

| 文件 | 内容 |
|---|---|
| [`subtitles/dario_en.srt`](subtitles/dario_en.srt) | 327 条英文字幕，UTF-8，20,929 B，已对齐到原片时基 |
| [`subtitles/dario_en_script.txt`](subtitles/dario_en_script.txt) | 英文旁白全文（1501 词），53 段，带段级时间轴与词数 |
| [`assets/credit.ass`](assets/credit.ass) | 片头署名字幕文件（可用 `tools/s8_credit.py` 重建） |

**脚本（12 个，Python 3.13）**

| 脚本 | 职责 |
|---|---|
| `tools/s0_timebase.py` / `s0b_fine.py` / `s0c_solve.py` | 用互相关标定母版与数据文件的 **+3.04 s** 偏移，解出全局时基 |
| `tools/s1_manifest.py` | 生成 53 段清单（起止、时长、原文） |
| `tools/en_clauses.py` | 英文译文的语义切分（`EN` 常量） |
| `tools/s2_clauses.py` | 把英文段落切分为 TTS 可读的短句单元 |
| `tools/s3_srt.py` | 生成 327 条 SRT（字级时间码 → 句子时间码） |
| `tools/s4b_tts_all.py` | 全量 TTS + 语速闭环求解 + 4 路并发（**核心脚本**） |
| `tools/s6_mix.py` | 人声铺轨 + 伴奏床 + 片尾接续 + 三级响度校验（**核心脚本**） |
| `tools/s8_credit.py` | 生成 `credit.ass` 片头署名 |
| `tools/s9_mux2.py` | 单遍压制：`ass=credit.ass` + `subtitles=dario_en.srt` 同时生效 |
| `tools/validate_srt.py` | SRT 结构与时间码合法性校验 |

依赖：`Python 3.13`、`edge-tts`、`numpy`、一个带 libx264 / libass / fontconfig 的 ffmpeg（GPL 构建，本项目实测用 `N-127957-g935f29eaae-20261023`）。

> **移植提示**：脚本里的本地绝对路径（`D:\ffmpeg`、`work/tools/...`）是原运行环境的路径。换机器时**只改路径，不要改逻辑**——语速闭环、拼接点、增益、限幅参数都是实测出来的定值。

## 技术参数 / Technical specs

**文本层**

- 中文 2535 字 → 英文 1501 词，语义等价翻译，保留原文的讽刺语气与术语
- 切分为 **53 段**，与上游 `数据/ch*.js` 的 53 段严格一一对应（`charTimes` 长度 == 文本长度 + 1，53/53 命中）
- 章节结构沿用原作五章，章偏移：ch1=0、ch2=190.5333、ch3≈353.83、ch4=421.86667、ch5≈518.87（**ch3/ch5 为推算值**，由上三章的等差结构反推，非上游明示）

**声音层**

| 项 | 值 |
|---|---|
| TTS 引擎 / 音色 | `edge-tts` / `en-US-AndrewMultilingualNeural` |
| 段数 / 失败数 | 53 / 0 |
| 语速拟合 | 物理模型 `dur ≈ A / (1 + rate/100)`，取多次调用中位数反解，容差 1.3% |
| 拟合精度 | 中位偏差 **0.50%**，p90 **1.50%**，最大 **8.8%**（S23） |
| 轻微压缩 | **22 段**用 `atempo` 收口，范围 1.0009–1.0888（最大 S23 = 1.0888） |
| 干声电平 | −21.0 / −21.0 / −21.4 LUFS，峰值 −3.3 ~ −4.2 dBFS → 单一全局增益即可 |
| 采样率 / 声道 | 48000 Hz 立体声 |
| 伴奏床增益 | **−6.3 dB** → 约 −26.1 LUFS |
| 人声增益 | **+5.0 dB** → 约 −16 LUFS |
| 人声限幅 | `alimiter=level=0:latency=1:limit=0.78`（`level=0` 必须显式指定，否则默认自动加 +1.8 dB） |
| 人声/伴奏分离度 | 约 10 LU |
| ducking / sidechain | **不使用**（会明显抽吸，改为固定增益） |
| 段间间隙 | 0.06 s |
| 母版拼接点 | **676.4417 s**（= 真数字静音区间 672.326–680.558 s 的中点） |
| 混音前直出 | I −13.7 LUFS / TP +3.0 dBTP / LRA 4.5 LU |
| **最终响度** | **I −15.5 LUFS / TP −2.5 dBTP / LRA 4.5 LU**，立体声峰值 0.7400，过采样越界 0 次 |

> 拼接点为什么是 676.4417 s：母版 703.928 s，而作曲脚本的覆盖只到约 680 s，片尾 22.3 s（字幕卡 + 配乐）必须从母版音轨直接截取。初版计划在 681.67 s 切入，结果**切掉了一个音符**——那里正好在一段渐强中。改为扫描全曲最长的数字静音段（672.326–680.558 s，对应作曲脚本的 `TAIL=7.0`），取中点切入；配乐在 680.558 s 才渐入，因此不会切断任何音符。

**画面层**

| 项 | 值 |
|---|---|
| 字幕条数 / 词数 | **327** 条 / 1501 词 |
| 字幕样式 | `Segoe UI Semibold`，FontSize 14（libass PlayResY=288 → 1080p 实际约 52.5 px 基线） |
| 描边 / 阴影 | Outline 1.4 / Shadow 1.4，黑描边、半透明黑阴影 |
| 位置 | `MarginV=28`（底部） |
| 片头署名（中） | `英文翻译及后期：@zihao_ZiO`，Noto Serif SC 48，RGB(165,180,183)，Y 860 |
| 片头署名（英） | `English translation & post-production: @zihao_ZiO`，Noto Serif SC 44，RGB(120,140,144)，Y 916 |
| 署名出现区间 | **帧 7–90（0.233–3.000 s）**，第 91 帧（3.033 s）随卡片一起切走 |

署名行的颜色不是估的：原卡存在三级亮度（大标题 p99≈226 / 中文署名 p99≈176 / 英文署名 p99≈134），直接套标题色会明显偏亮，因此按行取 p98/p99 采样。

**封装层**

| 项 | 硬字幕版 | 软字幕版 |
|---|---|---|
| 大小 | 701,647,596 B（669.1 MiB） | 778,792,812 B（742.7 MiB） |
| 视频 | libx264，CRF 18，preset slow，yuv420p，High@4.1，`aq-mode=3`，7778 kb/s | **`-c:v copy` 无损复制** |
| 音频 | AAC LC 192k → 实测 187 kb/s，48 kHz 立体声 | 同 |
| 字幕 | **烧录进画面** | mov_text 软字幕轨 |
| 片头署名 | **有** | **无** |
| 时长 | 703.94 s | 703.94 s |
| 其他 | `+faststart`，`-metadata title=Dario Genesis (English dub)` | 同 |

## 已知限制 / Known limitations

1. **画面内中文未翻译。** 部分镜头内部有中文文字（如「提交申诉」的后台界面、祖冲之割圆的纸面标注）。这些是画面像素的一部分，不是字幕层，翻译需要重渲染或逐帧遮挡。经评估：上游 40 个镜头只公开了 4 个母版原型，`production/` 从未发布，**重渲染整片不可行**；人工遮挡重制需 2–4 周。**决定：保留中文，作为「中文风味」接受。**
2. **配音是 TTS，不是真人。** 已做到逐段语速贴合与统一电平，但韵律与情感不及真人配音。
3. **上游只公开了 4/40 个镜头的母版。** 本项目的所有工作都建立在**已发布的成品视频**之上，不依赖也无法依赖上游的合成管线。
4. **软字幕版没有片头署名。** 因为该版视频流是 `-c:v copy`，无法叠加字幕层。署名只存在于主发布版与仓库文档中。
5. **章节偏移 ch3 / ch5 是推算值**（由 ch1/ch2/ch4 的等差结构反推），非上游明示。
6. **本译文未经过母语审校流程**，仅由译者本人校对。欢迎在 Issues 中提出修改建议。

## 许可 / License

**分三层，一层都不能改：**

| 内容 | 许可 | 文件 |
|---|---|---|
| `tools/*.py` | **MIT** | [`LICENSE-CODE`](LICENSE-CODE) |
| `subtitles/`、英文旁白稿、视频成品 | **CC BY-NC-SA 4.0** | [`LICENSE`](LICENSE) |
| `README.md`、`NOTICE.md`、`docs/` | **CC BY 4.0** | 本节声明 |

- **内容层不得放宽。** 英文字幕与英文旁白稿派生自上游 CC BY-NC-SA 4.0 的旁白文稿，因此**不能**改为 MIT / CC BY / 公有领域——这是 ShareAlike 的强制要求。
- **代码层可以自选。** `tools/` 是独立原创（未复制上游代码），选 MIT 是为了与上游代码层保持一致，属主动选择而非义务。
- 上游代码层（MIT）与上游文档层（CC BY 4.0）均未被本项目复制或再分发，因此不涉及。

**许可原文**：[CC BY-NC-SA 4.0 法律文本](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode) · [人类可读摘要](https://creativecommons.org/licenses/by-nc-sa/4.0/) · [MIT](https://opensource.org/license/mit)

**非商业（NC）**：禁止广告分成、付费墙、会员专享、付费打包、赞助商位、任何形式的内容变现；本仓库不设任何赞助、捐赠或付费入口。若后续需要商用，必须另行取得原作者授权。

**免责声明**：`Not endorsed by Anthropic.` 本项目与 Anthropic 无关，未获其认可或授权。标题与内容涉及真实公司名与真实人物，且属讽刺作品；该句防止内容被单独截图传播时脱离语境。

## 致谢 / Credits

- **原作 / Original work**：《达里奥创世录》(Dario Genesis) — [@你好与那啥](https://www.bilibili.com/video/BV1mEnb6LEnC)（bilibili），源码 [null0526/dario-genesis](https://github.com/null0526/dario-genesis)。画面、音乐、原始中文旁白文稿、视觉设计、时间轴数据、片头片尾卡片，全部出自原作者。
- **英文层 / English layer**：翻译、配音调度、字幕、混音、压制 — [@zihao_ZiO](https://github.com/ZiOstudio)。
- **工具链**：`edge-tts`（微软 Edge 神经网络 TTS）、FFmpeg（libx264 / libass / fontconfig）、libass、Noto Serif SC。

---

<sub>📄 项目完整记录：[`docs/项目全记录.md`](docs/项目全记录.md) · 上游设计审查：[`docs/设计审查与试水报告.md`](docs/设计审查与试水报告.md) · 若向上游索取源码所需材料：[`docs/原始工程需求清单.md`](docs/原始工程需求清单.md)</sub>
