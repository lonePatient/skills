# 作者与机构区翻译规范

`\author{}`（或 `\icmlaffiliation{}`、`\ijaffiliation{}` 等期刊宏）这一块经常踩坑。本文沉淀几条硬规则。

---

## 1. 不要碰原始的 `\author{}` 排版命令

- `\And` / `\AND` / `\thanks{}` / `\footnotemark[1]` / `\maketitle` / `\icmlauthorlist`：原样保留，不要重排。
- `\\` 强制换行同样保留——把它当作物理换行点对待。
- 模板（NeurIPS、ICML、IEEE、ACM 等）的样式会处理「姓名加粗、机构不加粗」「居中」「分栏」等版式行为；**翻译时不要替它们手写居中或加粗**，否则容易和模板冲突，出现「靠右」「上半段加粗、下半段不加粗」等怪异版式。
- **NeurIPS 默认就是首行作者名加粗、后续机构/邮箱不加粗**，这不是 bug，不要"修复"。如果用户问到，直接告知这是模板行为，并对比英文原稿即可。

---

## 2. 翻译什么、保留什么

| 内容 | 处理方式 |
|---|---|
| 作者姓名 | 一律不翻译，保留英文/拼音 |
| 学校 / 学院 / 实验室 / 公司 | 翻译为中文，并附英文原文 |
| 城市、国家 | 翻译为中文（"北京"、"中国"、"日本"），地名标准译名 |
| 邮箱 `\texttt{...}` | 保留 |
| 上下标符号 `^{1*}` `^\star` `^\dagger` | 保留 |
| 脚注内 `\thanks{...}` 中的英文说明 | 翻译为中文 |
| 「Equal contribution.」「Corresponding authors.」 | 翻译为「同等贡献。」「通讯作者。」 |

---

## 3. 机构译名的两种排版方式

### A. 短机构 → 一行内 `中文（English）`（首选）

机构名整体一行能放下时，直接用一行：

```latex
\textsuperscript{1}东京大学（The University of Tokyo），
\textsuperscript{2}理化学研究所先进智能项目（RIKEN Center for Advanced Intelligence Project, RIKEN AIP），
\textsuperscript{3}早稻田大学（Waseda University），
\textsuperscript{4}斯坦福大学（Stanford University）\\
```

或一作一栏的形式（NeurIPS 模板）：

```latex
\And
Noam Shazeer\footnotemark[1]\\
谷歌大脑（Google Brain）\\
\texttt{noam@google.com}\\
```

### B. 长机构 → 中文一行，英文换行一行（次选）

当英文机构名很长（>40 词）、放在 `（...）` 里会撑出右边距时，**改成两行**：第一行中文译名，第二行用 `\\` 起新行写英文原文。**英文用正体（无 `\textit{}` 修饰）**，可选 `\small` 缩字号。

```latex
$^{1}$北京理工大学空天智能信息处理科学与技术全国重点实验室，北京，中国\\
{\small (National Key Laboratory of Science and Technology on Space-Born Intelligent}\\
{\small Information Processing, Beijing Institute of Technology, Beijing, China)}\\[1pt]
$^{4}$武汉大学测绘遥感信息工程全国重点实验室，武汉，中国\\
{\small (State Key Laboratory of Information Engineering in Surveying, Mapping and}\\
{\small Remote Sensing, Wuhan University, Wuhan, China)}\\
```

在英文一行装不下时，按词义切到下一行：「Intelligent」之后断、「Mapping and」之后断，避免拆开短语。

### 选哪种？

> 简单判断：放进 `（...）` 之后这一整行会不会撑出页边？会就用 B，不会就用 A。

---

## 4. 中文译名顺序

中文里的自然顺序是 **大-中-小**：`大学 → 学院/实验室 → 城市 → 国家`。

```text
✓ 武汉大学计算机学院，武汉，中国
✓ 北京理工大学空天智能信息处理科学与技术全国重点实验室，北京，中国
✗ 计算机学院，武汉大学，武汉，中国              （读起来别扭）
```

英文原文遵循英文习惯（**Department, University, City, Country**），不要为了和中文对齐而改写英文括号里的内容，英文原文照抄即可。

---

## 5. 「Key Laboratory」译法 — 跟随中国 2022 改革

自 2022 年《科学技术进步法》修订生效后，**国家重点实验室**体系基本被**全国重点实验室**体系取代，绝大多数原 SKL 已重组为 NKL，政策文件中也不再使用「国家重点实验室」表述。

| 英文 | 中文译名（首选） |
|---|---|
| **National** Key Laboratory of ... | **全国**重点实验室 |
| **State** Key Laboratory of ...   | **全国**重点实验室（重组完成的旧 SKL）|
| MoE Key Laboratory of ...         | **教育部重点实验室** |
| 仅在罕见情况，该实验室明确尚未重组 | 仍可写「国家重点实验室」，并在脚注中说明 |

实务规则：**默认把两类 Key Laboratory 都译为「全国重点实验室」**；只有在能确认该实验室未参与重组（极少见），才保留旧名。

---

## 6. 字体修饰 — 严禁额外添加

- **正文**：原文出现 `\textit{}` / `\textbf{}` / `\emph{}` 时按位置保留，**翻译时不要新增**任何修饰命令。
- **作者/机构区**：括号里的英文机构名一律用 **正体（plain）**，不要套 `\textit{}` 或 `\emph{}`——这些命令是用来「强调」的，纯粹的对照译名不需要强调。
- **行间术语对照**：`视觉-语言模型（Vision-Language Models, VLMs）` 这类首次出现的术语对照，**括号里的英文也用正体**，与机构译名规则一致。
- **任务/术语本身就是 `\textit{}`** 的情况（例如表格表头 `\textit{Global Detection (GD)}`、`\textit{1024 × 1024 crop window}`）：原文就有的修饰必须保留，不要去掉。

简记：**「原文有就保留，原文没有就不加」**。

---

## 7. 中文版会比英文长 1.5–2x：默认拆行，不要硬挤一行

英文原作经常用 `\quad`（= 1em）作为同一行内分隔多个作者或多个机构的间距。换成中文后，**机构译名加上中英括号对照常常是英文原文的 1.5–2 倍长**，原本舒服的一行翻完会溢出右页边距。具体表现：

- 作者名行：5 个名字 + 4 个 `\quad` 在英文里勉强 fit textwidth，中译后 `\textsuperscript{}` 注脚加上 CJK 间距，最后一个名字会被切到页外。
- 机构行：`\textsuperscript{1}短机构 \quad \textsuperscript{2}中机构 \quad \textsuperscript{3}长机构` 通常超 textwidth，第 3 个机构溢出。

**翻译时默认的拆行策略**（按这个顺序选）：

1. **作者名**：每行不超过 3–4 个名字。原作 5+ 名字一行的，**一律拆**为 3-3-3 或 4-3-2 等。
2. **机构**：**每个机构占一行**（`\\` 结尾）。这是最稳的做法，永不溢出。如果机构都很短（例如 `\textsuperscript{1}清华大学 \quad \textsuperscript{2}北大`），可以两个一行；但只要有一个长机构，整列都拆成单行更安全。
3. 个别超长的（例如「微软「AI 向善」研究实验室（Microsoft AI for Good Research Lab）」），即便单独占一行也可能撑过居中宽度——这时改成 §3-B 的「中文一行 + 英文换行另一行」。

**反例（错误，会溢出）**：

```latex
\textsuperscript{1}Taylor 地理空间研究院（Taylor Geospatial） \quad
\textsuperscript{2}慕尼黑工业大学（Technical University of Munich） \quad
\textsuperscript{3}微软「AI 向善」研究实验室（Microsoft AI for Good Research Lab） \\
\textsuperscript{4}艾伦人工智能研究院（Allen Institute for AI） \quad
\textsuperscript{5}Vector 研究院（Vector Institute） \quad
\textsuperscript{6}卡尔顿大学（Carleton University） \quad
\textsuperscript{7}克拉克大学（Clark University）\\
```

**正例（每机构一行）**：

```latex
\textsuperscript{1}Taylor 地理空间研究院（Taylor Geospatial）\\
\textsuperscript{2}慕尼黑工业大学（Technical University of Munich）\\
\textsuperscript{3}微软「AI 向善」研究实验室（Microsoft AI for Good Research Lab）\\
\textsuperscript{4}艾伦人工智能研究院（Allen Institute for AI）\\
\textsuperscript{5}Vector 研究院（Vector Institute）\\
\textsuperscript{6}卡尔顿大学（Carleton University）\\
\textsuperscript{7}克拉克大学（Clark University）\\
```

**为什么 `tabular{c}` 会溢出而不是自动换行**：作者块通常包在 `\begin{tabular}{c}...\end{tabular}` 里，`tabular` 的列宽是按**最长行**取的，**不会自动换行**——一行内容超 textwidth 就直接溢出页面。所以必须人工 `\\` 切到下一行。

---

## 8. 译后自检清单

| 检查项 | 期望 |
|---|---|
| `\author{}` 内是否有手写的 `\begin{center}` 或 `\centering` | 应该没有；模板会自己居中 |
| 是否新增了 `\textit{...}` 包裹括号里的英文 | 应该没有 |
| 「State Key Laboratory」是否还残留译为「国家重点实验室」 | 应该没有（除非明确未重组） |
| 长机构是否会撑出右边距 | **必须**用 PDF 渲染首页 PNG 确认，必要时按 §3-B 拆行 |
| 作者名行长度是否超过 textwidth | 名字 + `\textsuperscript{}` + `\quad` 加起来超 textwidth 必溢出，按 §7 拆行 |
| 「同等贡献」「通讯作者」是否翻译了 | 应该翻译 |
| 邮箱、ORCID、`^{1,2\dagger}` 等符号是否原样保留 | 应该保留 |

**最直接的方法**：编译完成后用 PyMuPDF 渲染首页 PNG 看一眼（不是看 exit code，是真的用眼睛过一遍），确认作者块整体居中、英文不溢出、行与行之间不相互重叠。
