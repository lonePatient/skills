---
name: arxiv-paper-translator
description: 把 arXiv 论文自动翻译为中文 PDF 的 arxiv-paper-translator skill。触发后按本 skill 四步顺序直接执行，勿长篇规划。用户提供论文标题或 arXiv ID、说「翻译论文」「我想读中文版」等时立即使用。支持本地 xelatex 与在线编译双引擎、英文原文 _zh 副本对照、多篇并行处理。每篇论文文件夹同时保留英文原文 PDF 与中文译文 PDF。无需用户手动操作。
---

# arXiv Paper Translator（ChineseXiv）：arXiv 论文中文翻译

**目标：** 将指定论文的 LaTeX 源码译为中文，并编译得到 PDF。

**流程：** 须严格按下文「第一步」至「第四步」顺序执行，不得擅自省略、合并或调换步骤。

**交互：** 仅在论文 ID 无法确定、检索结果存在多个需用户择一才可向用户提问；其余情况一律无中断的执行得到最终翻译后的PDF。

**翻译：** 翻译全部由当前对话模型自身完成，严禁使用外部翻译工具以及下载已有的翻译版本。

---

## 第一步：确定论文 ID

- arXiv URL/ID → 直接提取 ID
- 论文标题 → 搜索 arXiv / 网页查找 ID；找不到时给出候选让用户确认

---

## 第二步：获取源码

```bash
python3 {SKILL_DIR}/scripts/download.py "{PAPER_ID}" "$OUTPUT_DIR/source"
```

`download.py` 一步完成：下载源码 → 解压 → 递归查找 `.tex` → 定位主文件 → 提取标题 → 把主文件以及它通过 `\input{}` / `\include{}` 引用的子 `.tex` 文件都复制为 `_zh.tex` 副本，并把 zh 主文件里的 input 引用一并改写到 `_zh` 版本 → **直接下载 arXiv 官方编译好的英文 PDF**（按英文标题命名）落在 `source/` 同级目录，稍后与中文译稿 PDF 并排存放。

### `OUTPUT_DIR` 的命名约定

用户通常给出**父目录**（例如 `~/papers`、`~/projects/paper-reading`）。约定每篇论文落在一个**独立子目录**下，命名为 `{paperid}-{中文标题}`，目录里**同时**放英文原文 PDF 与中文译文 PDF：

```
~/projects/paper-reading/
├── 1706.03762-你所需要的只是Attention/
│   ├── source/
│   ├── Attention Is All You Need.pdf        ← 英文原文（arXiv 官方 PDF，download.py 自动下载）
│   └── 你所需要的只是Attention.pdf            ← 中文译文（compile.py 编译）
└── 2605.17792-HydroAgent_基于模拟器驱动…/
    ├── source/
    ├── HydroAgent_Bridging the Gap….pdf      ← 英文原文
    └── HydroAgent_基于模拟器驱动….pdf          ← 中文译文
```

由于中文标题在翻译完成前不可知，按下列两阶段处理：

1. **下载阶段**：先用 `$OUTPUT_DIR = $PARENT/$PAPER_ID` 占位（**只用 arXiv ID，无标题后缀**）。
2. **翻译完成、确定 `\title{}` 中文标题后**：把整个目录从 `$PARENT/$PAPER_ID` 重命名为 `$PARENT/$PAPER_ID-$PDF_NAME_ZH`，再调用 `compile.py` 把 PDF 写到新目录里。`$PDF_NAME_ZH` **不是** `\title{}` 的原样，而是把 `\title{}` 里的全角 `：` 替换为 `_`（详见第三步「文件系统命名」），例如 `\title{HydroAgent：基于模拟器驱动……}` → `$PDF_NAME_ZH=HydroAgent_基于模拟器驱动……`。

   ```bash
   mv "$PARENT/$PAPER_ID" "$PARENT/$PAPER_ID-$PDF_NAME_ZH"
   OUTPUT_DIR="$PARENT/$PAPER_ID-$PDF_NAME_ZH"
   WORK_DIR="$OUTPUT_DIR/source"
   ```

若用户只翻一篇论文，没有「父目录」语义（例如直接说「放到 `~/Desktop`」），保持 `$OUTPUT_DIR = ~/Desktop/$PAPER_ID-$PDF_NAME_ZH` 即可。**不要把多篇论文的 `source/` 直接堆在同一个父目录里**——会互相覆盖。

源码统一落在 `$OUTPUT_DIR/source/`（不再使用 `.tmp_arxiv` 之类的临时名）。

无源码（仅 PDF）则告知用户跳过。

脚本向 stdout 输出六行，格式如下：
```
WORK_DIR=<源码目录绝对路径，即 $OUTPUT_DIR/source>
MAIN_TEX=<英文原始主文件相对路径，只读快照>
MAIN_TEX_ZH=<供翻译的中文主文件相对路径（download.py 已自动复制好）>
PDF_NAME=<论文英文标题（仅供生成备用名）>
PDF_NAME_EN=<英文原文 PDF 的跨平台安全文件名，冒号等已替换为 _>
PDF_EN=<已下载的英文 PDF 绝对路径；若没下到则为空字符串>
```

`MAIN_TEX` 永远是英文原文，**永远不要修改**；翻译只动 `MAIN_TEX_ZH` 及其 `_zh` 子文件。两者并列存放，方便对照。

### 英文原文 PDF（强制：必须与中文译文同在一个文件夹）

每个论文文件夹里**必须**同时有「英文原文 PDF」和「中文译文 PDF」，缺一不可。英文原文 PDF 的获取分两条路，**按优先级**走：

1. **首选——直接下载 arXiv 官方 PDF（download.py 已自动完成）。** arXiv 已编译好的 PDF 是作者最终排版、最忠于原貌的版本，比本地重编英文源码更稳更快。`download.py` 会把它按 `PDF_NAME_EN` 命名，落在 `source/` 同级（即 `$OUTPUT_DIR`）。成功时 `PDF_EN` 是该文件的绝对路径。
2. **回落——本地编译英文源码（仅当 `PDF_EN` 为空时）。** 极少数论文官方 PDF 取不到，此时在第四步（目录已重命名、工具链已就绪）顺带用 `compile.py` 编译只读的英文 `$MAIN_TEX`：

   ```bash
   # 仅当 download.py 的 PDF_EN 为空时执行；MAIN_TEX 无中文，compile.py 不会注入 CJK，按原貌编译
   python3 {SKILL_DIR}/scripts/compile.py "$WORK_DIR" "$MAIN_TEX" "$OUTPUT_DIR/$PDF_NAME_EN.pdf" --engine auto
   ```

英文 PDF 命名约定 `PDF_NAME_EN`（`download.py` 已按此实现，跨平台/网盘/Git/URL 均安全）：以英文标题为基础，**半角/全角冒号 `:`/`：` → `_`**（与中文目录命名的方法名分隔同构，如 `GeoGround: ...` → `GeoGround_...`），**空格 → `_`**（不留空格，免去 shell/URL 转义），标题里**原有的连字符 `-` 保留**（如 `Vision-Language`，与代表空格的 `_` 区分，便于还原原题），其余 `<>"|?*` 等不安全字符 → `_`。最终形如 `GeoGround_A_Unified_Large_Vision-Language_Model_for_Remote_Sensing_Visual_Grounding.pdf`，与中文 PDF `GeoGround_面向遥感视觉定位的统一大型视觉-语言模型.pdf` 同享 `GeoGround_` 前缀、一眼成对；两份文件名天然以语言区分原文与译文。

> 收尾自检：进入第四步「清理」前，**务必确认** `$OUTPUT_DIR` 下既有 `$PDF_NAME_EN.pdf`（英文原文）又有 `$PDF_NAME_ZH.pdf`（中文译文），**且两者内容范围一致**（若中文版取消注释纳入了补充材料/附录，英文也必须是含补充材料的版本，见第三步）。只有中文、缺英文（或反之）、或中英内容范围不一致，都算未完成。

---

## 第三步：翻译

由当前**对话模型**直接对 `$WORK_DIR/$MAIN_TEX_ZH`（以及它 input 进来的 `_zh` 子文件）进行翻译修改。`$MAIN_TEX` 是英文只读快照，**永远不要修改**。按以下规则翻译：

- **翻译范围：** 默认翻译全文，包括 `\appendix` 之后的附录内容。用户明确要求「只翻正文」「不翻附录」时，才在 `\appendix` 之前停止翻译。**留意源码里「写好却被 `%` 注释掉的补充材料/附录」**（arXiv 版常见：作者把 supplementary 注释掉以压缩正文页数，`download.py` 仍会把它复制成 `_zh` 子文件）——这类内容 arXiv 官方英文 PDF 往往不含，但源码既已写好，可在用户要求或同意时取消注释、一并翻译编译，让中文版比 arXiv PDF 更完整；取消注释前先确认其引用的图表资产（`fig/` 等目录下）齐全，再编译。**关键：中文版一旦纳入补充材料，英文 PDF 也必须同步含补充材料才能逐页对照** —— 复制英文主文件为 `main_en.tex`（**不动只读的 `$MAIN_TEX`**），在副本里取消同样的 `\input{...}`，再用 `compile.py` 编译覆盖原英文 PDF。
- **必须翻译：** 正文叙述、摘要、图表标题、列表项、脚注中的描述文本、代码块中的注释；附录 `tcolorbox` / `lstlisting` / prompt example 里的**自然语言提示词、角色说明、步骤说明、动作说明、表头说明**也要翻译（这是论文内容，不是“代码本体”）；**机构名**（如「斯坦福大学（Stanford University）」）与**描述性方法名/模块名**（如「自适应检索模块（Adaptive Retrieval Module, ARM）」）也要中译，按下方「术语首次出现规则」给出中英对照。
- **保留不翻：** 数学环境、LaTeX 命令、`\cite{}`/`\ref{}`/`\label{}`、图片路径、URL、`.bib`、**代码本体中的标识符 / JSON key / API action name / XML tag / 占位符**（如 `action_type`、`open_app`、`<tool_call>`、`<instruction_here>`）、**人名**、**专有模型名**（GPT-4、LLaMA、Qwen、DeepSeek 等已成符号的型号）、**专有数据集/基准名**（ImageNet、MMLU、GSM8K 等）。不要把整段 prompt 模板误判为代码而原样保留；只保留其中必须机器可读或示例结构相关的 token。
- **不要新增字体修饰：** 严禁额外添加 `\textit{}`、`\textbf{}`、`\emph{}` 等格式命令——只在原文已存在时按位置保留。括号里的英文机构名、英文术语原文一律用 \textbf{正体（plain）}，不要套 `\textit{}`；括号内的英文只是为方便对照，不属于「需要强调」的内容。
- **专有名词：** Transformer、Softmax、Token、Attention、Self-Attention、Multi-Head Attention、Scaled Dot-Product Attention 等已通用化的学术术语**严格保留英文**，不要硬译为「转换器 / 注意力 / 自注意力 / 多头注意力」等。复合词同样保留：`Multi-Head Self-Attention`、`Restricted Self-Attention`、`Encoder Self-Attention` 等都不要拆译。其它领域的同类约定俗成术语（CNN、RNN、LSTM、Embedding、Token、Logits、Softmax、Dropout、BLEU 等）同理。
- **术语首次出现规则（重要）：** 全文术语、符号、代号需统一；非通用新名词、新术语、新概念在**首次出现**时给出清晰说明。
  - 反复出现（≥2 次）的较长词组，在**首次出现**时写作「中文全称（English Full Name, ABBR）」，例如「灾害行动响应智能体（Disaster Operational Response Agent, DORA）」，之后全文统一用缩写 `ABBR` 或中文简称；
  - 全文仅出现一次的，直接用中文全称即可，必要时在括号中附英文全称（不加缩写）；
  - **摘要与正文各自独立统计**：同一术语若在摘要和正文中都是首次出现，两处都要分别注明完整定义，确保摘要可以独立阅读。
  - 仅有缩写而无英文全称的写法（例如「MCP 库」「SAR 影像」）必须替换为定义形式。
- **标题要求：** `\title{}` 须改为自然中文题名，不保留英文原题或中英并列。**标点忠于原文**——原标题里的 `:` 翻成中文标准的全角 `：`（中文排版规范），不要省略也不要替换为 `-`。**若原标题以专有方法名/系统名/产品名领起**（如 `HydroAgent: ...`、`DORA: ...`、`LLaMA-Factory: ...`），中文 `\title{}` 必须保留该专有名词作为前缀，写作「专有名（英文原样）：中文副标题」，例如 `HydroAgent：基于模拟器驱动强化学习……`；不要把专有名翻成中文，也不要丢掉。
- **文件系统命名（与 `\title{}` 解耦）：** PDF 内部 `\title{}` 遵循上一条；但**目录名与 PDF 文件名要替换非 ASCII 标点**以保证跨平台（Windows、网盘、Git 都不接受裸 `:`/`：`）。采用两层分隔：
  - 外层 `-`：arxiv-ID ↔ 标题主体，例如 `2605.17792-HydroAgent_...`
  - 内层 `_`：英文方法名 ↔ 中文副标题，**替换 `\title{}` 中的全角 `：`**，例如 `HydroAgent_基于模拟器驱动…`
  - 完整范例：`2605.17792-HydroAgent_基于模拟器驱动强化学习缩小前沿LLM与人类专家在水文模型率定中的差距/` 内含同名 `.pdf`。
  - 两层分隔的目的是视觉上区分语义层级（ID/方法名/副标题）；全用 `-` 会出现 `ID-Method-Subtitle` 三段同形分隔，边界不清。`_` 与 `-` 都全平台安全。
  - 若原标题**没有**专有方法名前缀（纯描述性中文标题），直接 `$PAPER_ID-$PDF_NAME_ZH` 即可，不需要内层 `_`。
- **多篇处理：** 多篇论文可以分别处理；只有在用户**明确要求**并行委派时，才开启多个 subagent，否则直接顺序完成。

译后必须做自检（默认 full 模式扫描全文，扫描的是中文翻译目标文件）：

```bash
python3 {SKILL_DIR}/scripts/inspect_tex.py scan "$WORK_DIR" "$MAIN_TEX_ZH" full
```

若用户明确要求「只翻正文」，则改为：

```bash
python3 {SKILL_DIR}/scripts/inspect_tex.py scan "$WORK_DIR" "$MAIN_TEX_ZH" body
```

脚本会输出 `SUSPECT_COUNT=<数字>` 以及若干 `SUSPECT=<文件>:<行号>:<片段>`。
- 只要 `SUSPECT_COUNT` 非 0，就必须逐条回到对应位置进行翻译；
- 只有 `SUSPECT_COUNT=0`，或剩余项明确属于「保留不翻」范围时，才可进入第四步。

### 第三步执行检查清单

进入第四步前，逐项确认：

- [ ] 已按规则翻译正文、摘要、图表标题、列表项、脚注、附录自然语言提示词。
- [ ] 数学环境、LaTeX 命令、图片路径、URL、代码标识符 / JSON key / XML tag / 占位符等保留未翻。
- [ ] 术语首次出现已按「中文全称（English Full Name, ABBR）」格式给出，摘要与正文分别统计。
- [ ] 通用学术术语（Transformer、Attention、Softmax 等）未强行中译。
- [ ] `\title{}` 已改为自然中文题名，专有方法名前缀保留，全角冒号使用正确。
- [ ] 未新增 `\textit{}` / `\textbf{}` / `\emph{}` 等字体修饰命令。
- [ ] 作者/机构块已按 `references/author-block.md` 处理，长机构已拆行。
- [ ] `inspect_tex.py` 扫描结果 `SUSPECT_COUNT=0`，或剩余可疑项均属「保留不翻」范围。

---

## 第四步：编译、修表、目检与清理

本步骤拆为 5 个顺序动作：**目录重命名 → 编译 → 表格溢出扫描 → 排版目视自检 → 清理交付**。前一步不完成，不要进入下一步。

### 4.1 目录最终命名

在编译前，按第二步的命名约定，把 `$OUTPUT_DIR` 从 `$PARENT/$PAPER_ID` 重命名为 `$PARENT/$PAPER_ID-$PDF_NAME_ZH`，使整篇论文（含 `source/` 子目录、第二步已下载的英文原文 PDF）都落在最终目录里。`$PDF_NAME_ZH` 基于翻译后的 `\title{}` 自然命名，与 `\title{}` 一致或更精炼。最终中文 PDF 直接落在 `$OUTPUT_DIR/$PDF_NAME_ZH.pdf`，与 `source/`、英文原文 PDF 同级。第二步下载的 `$PDF_NAME_EN.pdf` 在 `$OUTPUT_DIR` 内，整体 `mv` 时会自动跟着搬到最终目录，无需单独处理。

```bash
python3 {SKILL_DIR}/scripts/compile.py "$WORK_DIR" "$MAIN_TEX_ZH" "$OUTPUT_DIR/$PDF_NAME_ZH.pdf" --engine auto
```

**英文原文 PDF 兜底**：若第二步 `PDF_EN` 为空（官方 PDF 没下到），在这里顺带补一份英文 PDF，确保最终目录里中英两份都在：

```bash
[ -z "$PDF_EN" ] && python3 {SKILL_DIR}/scripts/compile.py "$WORK_DIR" "$MAIN_TEX" "$OUTPUT_DIR/$PDF_NAME_EN.pdf" --engine auto
```

**`--engine` 选项**（默认 `auto`）：
- `auto`：先检测本地是否装有 `xelatex`，装了就用本地编译；未装则回落到在线服务。**首选**。
- `local`：强制本地 `xelatex` 编译；未装 `xelatex` 直接报错。适合环境齐全 + 想完全离线的场景。
- `online`：强制走 `latex.ytotech.com` 在线编译。适合本地 TeX 环境缺包、或者想保留旧行为。

用户可以在调用时通过自然语言指定（例如「用在线编译」「强制本地编译」），否则一律传 `--engine auto`。

`compile.py` 会统一完成以下编译前处理（两种引擎共用）：
- 默认使用 `xelatex` + `xeCJK` 编译栈；若检测到中文且主文件尚无 CJK 支持，自动注入 `fontspec` / `xeCJK` / `\setCJKmainfont{Noto Serif CJK SC}`；
- 自动注释掉与 Unicode 编译栈冲突的 `fontenc` / `inputenc`；
- 自动识别 `bibtex` / `biber` / 已内置 `.bbl` 的情况；
- 自动忽略常见编译中间文件、`build/` 子目录以及未被源码引用的游离 PDF（在线引擎下避免把无关产物上传；本地引擎下避免污染源码目录）。

编译失败时：读取 stderr 中的错误日志，参考 `references/compile-errors.md` 修复源码，重新编译（最多重试 2 次）。

**编译成功不代表排版通过**：xelatex exit 0 但日志里 `Overfull \hbox` 经常是中英换算带来的表格/段落溢出，目视才能发现。**强制**执行下一步「表格溢出扫描」。

**本地手动重编（应急）：** `source/build/` 子目录是本地 xelatex 中间产物的约定输出位置。手动重编命令：

```bash
cd "$OUTPUT_DIR/source"
xelatex -output-directory=build "$MAIN_TEX_ZH"
BIBINPUTS=".:$BIBINPUTS" bibtex "build/${MAIN_TEX_ZH%.tex}"
xelatex -output-directory=build "$MAIN_TEX_ZH"
xelatex -output-directory=build "$MAIN_TEX_ZH"
cp "build/${MAIN_TEX_ZH%.tex}.pdf" "../$PDF_NAME_ZH.pdf"
```

### 表格溢出扫描（强制，**先于目视**做）

中文方块字宽度约为英文比例字体的 1.5–2 倍。原作按英文宽度调好的 `\small / \tabcolsep` 在中文下普遍宽度溢出 5–20%，**不修就一定出现表格压到对面栏中文上**。

```bash
grep -E "Overfull \\\\hbox \([0-9]+\.[0-9]+pt" "$WORK_DIR/build/${MAIN_TEX_ZH%.tex}.log" \
    | awk -F'[()]' '$2+0 > 5 {print}'
```

每条 `Overfull \hbox (XX.XXpt too wide) in paragraph at lines AAA--BBB`：

1. 把 `AAA--BBB` 行号区间映射到 `$MAIN_TEX_ZH` 里的某个外层 `\begin{tabular}` 块（注意：行首才是外层；带 `[c]{@{}c@{}}` 出现在行中的是 `\makecell` 内嵌表头，**不要包**）。
2. 用 `\resizebox{\linewidth}{!}{ ... }` 把整个外层 `\begin{tabular}...\end{tabular}` 块包住。`\linewidth` 在 `table` 里等于栏宽、在 `table*` 里等于页宽，**一段代码窄表宽表通吃**。
3. 重新编译。第一轮过后 `> 5pt` 的 Overfull 应该接近归零。

为什么是 `\resizebox{\linewidth}` 而不是「全文 `\scriptsize`」「手工调列宽」：它**只对真正超宽的表起作用、按比例保留作者意图、且小表不被强行拉宽**——可以稳定地批量自动化，不必逐表手工权衡。完整方法论与边界情况见 `references/table-overflow.md`。

剩余「溢出 > 20%」或「`\resizebox` 后字号过小」的少数情况，按 `references/table-overflow.md` 的二级手段顺序处理（先压 `\tabcolsep`，再压 `\arraystretch`，再精简表头，最后才考虑横版或拆表）。

### 排版自检（强制）

编译成功后**必须**渲染至少首页与含「作者块」「宽表格」「wrapfigure」的页面，确认中文版排版未崩坏。**不能凭借** exit code 0 就认定编译成功——CJK 与英文模板互动经常导致内容溢出页边距、文字相互重叠这类**仅渲染才能看出来的问题**。

```python
import fitz  # PyMuPDF
doc = fitz.open("$OUTPUT_DIR/$PDF_NAME_ZH.pdf")
for i in [0, ...]:  # 首页必看；含作者块、长 caption、多列表格的页都要看
    doc[i].get_pixmap(dpi=200).save(f"/tmp/check_p{i+1}.png")
```

然后用 Read 工具把这几张 PNG 实际过一遍眼睛，确认：

- [ ] **作者块** 没有溢出右边距（中文机构名通常比英文长 1.5–2x，原作 5 个名字 + `\quad` 一行的排版换成中译后常常溢出；按 `references/author-block.md` 调整）。
- [ ] **多列表格** 没有任何单元格内文字被压成竖排、数字互相粘连或与边框重叠（中文字符高且方，原作 `m{1.10cm}` / 13 列 benchmark 表在中译后多半装不下；日志无严重 Overfull 也可能视觉失败，按 `references/table-overflow.md` 的“视觉失败但日志干净”范式处理：**先试竖版紧凑方案并渲染确认**，只有竖版仍不可读或字号低于底线时，才用 `pdflscape` 横向页）。
- [ ] **wrapfigure / wraptable / sidefig** 没有被切断、没有与正文或相邻 figure 重叠；若 wraptable 与右侧图/双栏浮动互相压住，优先改为普通 `table` 或移动浮动体，不要硬留 wrap。
- [ ] **tcolorbox / lstlisting / prompt example** 内容在框内完整可读；自然语言提示词已经翻译，JSON key / XML tag / placeholder 等机器可读 token 保留；统一使用 `promptstyle`，避免每个框各写一套选项。
- [ ] **图注与表注** 完整可读，加粗段没断行到奇怪位置。

发现问题就回到译稿上调整 LaTeX 结构（不是改翻译文字），然后重编。直到目视确认没有崩坏，才算「编译成功」。

### 清理中间产物

编译并目视确认后，再清理（删除 `source/build/` 与 inspect 临时文件，保留英文原文与翻译稿源码以便对照与手动重编）。**清理前最后确认 `$OUTPUT_DIR` 下中英两份 PDF 都在**（`$PDF_NAME_EN.pdf` + `$PDF_NAME_ZH.pdf`）：

```bash
python3 {SKILL_DIR}/scripts/cleanup.py "$OUTPUT_DIR"
```

cleanup.py **只清 `build/` 子目录内的中间产物**，不动 `source/` 根目录的任何文件——很多 arXiv 源码会直接附带预生成的 `main.bbl`（论文没发 `.bib`），这种 `.bbl` 属于原始源码，删了下次重编会出现一堆 `??`。

多篇论文时，所有论文都完成 PDF 编译并目视确认后再进行中间文件清理。

最后告知用户：
- 中文译文 PDF：`$OUTPUT_DIR/$PDF_NAME_ZH.pdf`
- 英文原文 PDF：`$OUTPUT_DIR/$PDF_NAME_EN.pdf`（arXiv 官方 PDF；个别论文取不到时为本地编译英文源码所得）
- 源码目录：`$OUTPUT_DIR/source/`（含英文原文 + `_zh.tex` 中文译稿，可手动重编）

---

## 参考文件
- `references/table-overflow.md`：**表格与中文重叠的诊断 + 修复范式**——为什么不能"一刀切缩小所有表"、怎么用 `Overfull \hbox` 日志精确定位、怎么用 `\resizebox{\linewidth}{!}{...}` 批量修、二级手段（`\tabcolsep` / `\arraystretch` / 表头精简 / 横版 / 拆表）顺序与边界。**每篇必跑的最后一道工序，读这个。**
- `references/framed-content.md`：**附录里 `tcolorbox`/`lstlisting` 的诊断 + 排版基线**——为什么中文长行会冲出框右边、为什么默认 box 看起来很糙、preamble 里 `\lstset{breaklines=true}` + `\tcbset{promptstyle/.style={...}}` 一处统一所有 box 风格、批量把 inline 选项压成 `promptstyle` 的脚本。**论文有 GPT 提示词/JSON 模板/对话样例附录时读这个。**
- `references/compile-errors.md`：编译常见错误、CJK 排版陷阱（宽表挤压、wrapfigure caption 溢出、`.bbl` 误删等）及修复方法。
- `references/author-block.md`：作者/机构区的排版与译名规范（短机构内联、长机构换行、`\textit` 禁用规则、「全国/国家重点实验室」译法、**中文版机构名长度是英文 1.5–2x 必须默认拆行**）。翻译机构/作者块前先读这个。
