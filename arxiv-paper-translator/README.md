# arXiv Paper Translator

将 arXiv 论文的 LaTeX 源码自动翻译为中文 PDF，同时保留英文原文 PDF 与翻译源码，方便对照与手动重编。

## 功能

- 通过 arXiv ID 或论文标题定位论文并下载源码。
- 自动准备 `_zh.tex` 中文翻译副本，英文原文件保持只读。
- 优先下载 arXiv 官方英文 PDF，与中文译文并排存放。
- 支持本地 `xelatex` 与在线 `latex.ytotech.com` 双引擎编译。
- 自动注入 CJK 支持、处理 `inputenc`/`fontenc` 冲突、识别 bibtex/biber/预编译 `.bbl`。
- 提供漏译扫描、表格溢出修复、排版目视自检等辅助脚本与参考文档。

## 安装

### 1. 克隆或下载本仓库

```bash
cd /path/to/arxiv-paper-translator
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

- `requests`：在线编译引擎必需。
- `pypdf`：可选，用于检测 PDF 中残留未解析引用标记。
- `PyMuPDF`：可选，用于排版自检时将 PDF 渲染为 PNG。

### 3. 安装本地编译器 xelatex（推荐）

本地编译比在线编译更稳定、更保护隐私。以下以 **macOS** 为主环境说明。

#### macOS

推荐通过 [MacTeX](https://tug.org/mactex/) 安装完整 TeX 发行版：

```bash
brew install --cask mactex
```

安装后可能需要刷新 PATH：

```bash
eval "$(/usr/libexec/path_helper)"
```

或在 `~/.zshrc` 中添加：

```bash
export PATH="/Library/TeX/texbin:$PATH"
```

验证安装：

```bash
xelatex --version
```

### 4. 安装中文字体

`compile.py` 默认使用 `Noto Serif CJK SC`。macOS 与大多数 Linux 发行版已预装；若编译报字体缺失，请安装：

- macOS：`brew install --cask font-noto-serif-cjk-sc`

## 缺少宏包时如何安装

使用 `xelatex` 编译时，若日志中出现 `File 'xxx.sty' not found`，说明当前环境缺少对应 LaTeX 宏包。处理方式如下：

### 方式一：使用发行版自带的包管理器（推荐）

#### TeX Live

```bash
tlmgr install xxx
```

例如缺少 `booktabs`：

```bash
tlmgr install booktabs
```

若 `tlmgr` 未初始化，先执行：

```bash
tlmgr init-usertree
```

#### MiKTeX

MiKTeX 通常会自动提示安装缺失宏包。也可手动安装：

```bash
miktex packages install xxx
```

或在 MiKTeX Console 图形界面中搜索并安装。

#### MacTeX

MacTeX 基于 TeX Live，同样使用 `tlmgr`：

```bash
sudo tlmgr install xxx
```

### 方式二：改用在线编译引擎

若本地安装宏包困难，可直接使用在线编译服务：

```bash
python3 scripts/compile.py <work_dir> <main_tex> <output_pdf> --engine online
```

> 注意：在线编译会上传完整 LaTeX 源码到 `latex.ytotech.com`，请勿用于敏感或尚未公开的论文。

### 方式三：查询在线包列表

在决定安装前，可先确认该宏包是否被在线服务支持：

```text
https://latex.ytotech.com/packages
```

### 常见缺失宏包示例

| 报错 | 安装命令 |
|---|---|
| `File 'xeCJK.sty' not found` | `tlmgr install xecjk` |
| `File 'fontspec.sty' not found` | `tlmgr install fontspec` |
| `File 'booktabs.sty' not found` | `tlmgr install booktabs` |
| `File 'multirow.sty' not found` | `tlmgr install multirow` |
| `File 'pdflscape.sty' not found` | `tlmgr install pdflscape` |
| `File 'tcolorbox.sty' not found` | `tlmgr install tcolorbox` |
| `File 'listings.sty' not found` | `tlmgr install listings` |
| `File 'biblatex.sty' not found` | `tlmgr install biblatex` |
| `File 'biber' not found` | `tlmgr install biber` |

## 快速开始

### 1. 下载论文源码

```bash
python3 scripts/download.py 1706.03762 /path/to/output/1706.03762/source
```

输出包含 `WORK_DIR`、`MAIN_TEX`、`MAIN_TEX_ZH`、`PDF_NAME`、`PDF_NAME_EN`、`PDF_EN` 六行变量赋值，可在脚本中 `eval` 使用。

### 2. 翻译

由当前对话模型直接修改 `MAIN_TEX_ZH` 及其 `_zh` 子文件，英文 `MAIN_TEX` 只读。

### 3. 漏译扫描

```bash
python3 scripts/inspect_tex.py scan /path/to/output/1706.03762/source main_zh.tex full
```

### 4. 编译

```bash
python3 scripts/compile.py /path/to/output/1706.03762/source main_zh.tex /path/to/output/1706.03762/中文标题.pdf --engine auto
```

### 5. 清理

```bash
python3 scripts/cleanup.py /path/to/output/1706.03762
```

## 目录结构

```text
arxiv-paper-translator/
├── SKILL.md                  # Skill 主文档：四步流程与详细规则
├── README.md                 # 本文件
├── requirements.txt          # Python 依赖
├── agents/
│   └── interface.yaml        # Skill 元数据：触发、输入输出、依赖、权限
├── scripts/
│   ├── download.py           # 下载 arXiv 源码与官方英文 PDF
│   ├── compile.py            # 本地/在线双引擎编译
│   ├── inspect_tex.py        # 漏译扫描
│   └── cleanup.py            # 清理编译中间产物
└── references/
    ├── table-overflow.md     # 表格溢出诊断与修复
    ├── framed-content.md     # tcolorbox/lstlisting 排版
    ├── compile-errors.md     # 常见编译错误与 CJK 陷阱
    └── author-block.md       # 作者/机构区翻译与排版规范
```

## 常见问题

**Q：本地没有 xelatex，能否使用本工具？**  
A：可以。`compile.py` 默认 `--engine auto`，未检测到 `xelatex` 会自动回落到在线编译。

**Q：在线编译超时或失败怎么办？**  
A：检查工作目录是否混入了无关大文件；优先改用本地 `xelatex` 编译。

**Q：编译成功但 PDF 里有 `??` 或 `[?]`？**  
A：说明引用未解析。检查 `.bbl` 是否被误删、bibtex/biber 是否正确执行，或参考 `references/compile-errors.md`。

**Q：表格压到正文上怎么办？**  
A：参考 `references/table-overflow.md`，首选 `\resizebox{\linewidth}{!}{...}` 包裹外层 `tabular`。

## 项目来源

本项目参考并改编自 [yuchenwu73/chinesexiv](https://github.com/yuchenwu73/chinesexiv)，用于将 arXiv 论文 LaTeX 源码自动翻译为中文 PDF。核心流程、脚本与参考文档在原项目基础上进行了扩展与工程化整理。
