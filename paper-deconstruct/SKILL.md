---
name: paper-deconstruct
description: Use when analyzing academic papers from arXiv or top-tier conferences, generating engineering-first, critical-thinking technical deconstruction reports. Triggers on "read paper", "analyze paper", "论文研读", "技术总结", "论文解析", "读论文", "分析论文", or when provided with LaTeX source, PDF, or arXiv URL.
---

# paper-deconstruct

面向工程复现与批判性思维的论文分析引擎，通过 6 阶段流水线（含第 3.5 步自检）生成 13 章节技术解构报告。

## 核心原则

工程优先的拆解 + 批判性深度。聚焦可复现细节，同时识别脆弱假设、反例与后续研究方向。

## 输入输出契约

**Inputs:** arXiv URL/ID, paper title, local LaTeX directory, or PDF fallback.
**Output:** `{YYYY-MM-DD}-{title}.md` final report plus intermediate files:
`01-parse.md`, `02-insights.md`, `03-draft.md`, `03-research-notes.md`, `03.5-validation.md`, `04-critique.md`, `05-revision.md`, and `figure_map.json`.
Final report frontmatter includes: title, quick summary (≤400 chars), paper link, institution info, open-source link, keywords. See [stage-06-polish.md](references/stage-06-polish.md) for the exact template.
**Language:** zh-CN; proper nouns stay in English.

## 工作流

| Stage | Output | Reference |
|-------|--------|-----------|
| 1. Parse | `01-parse.md` | [stage-01-parse.md](references/stage-01-parse.md) |
| 2. Insights | `02-insights.md` | [stage-02-insights.md](references/stage-02-insights.md) |
| 3. Draft | `03-draft.md` | [stage-03-draft.md](references/stage-03-draft.md) |
| 3.5. Self-Check | `03.5-validation.md` | [stage-03.5-validation-checklist.md](references/stage-03.5-validation-checklist.md) |
| 4. Critique | `04-critique.md` | [stage-04-critique.md](references/stage-04-critique.md) |
| 5. Revision | `05-revision.md` | [stage-05-revision.md](references/stage-05-revision.md) |
| 6. Polish | `{YYYY-MM-DD}-{title}.md` | [stage-06-polish.md](references/stage-06-polish.md) |

## 触发条件

Activate when user mentions:
- arXiv link/ID, PDF file, LaTeX directory, paper title
- "read paper", "analyze paper", "论文研读", "技术总结", "论文解析", "读论文", "分析论文"

## 边界

- In scope: arXiv / top-tier conference papers with accessible source or PDF
- Out of scope: pure philosophy, news, non-technical documents, papers without accessible content
- If only abstract available, mark the report as provisional and state limitations

## 关键约束

- 禁止杜撰；缺失信息标记为「未提供」。
- 禁止营销词汇。
- 禁止感叹号或情绪化形容词。
- 最终报告中的原始图片必须是 JPG/PNG。PDF 图片需先调用 `scripts/convert_figures.py` 转换。
- 专有名词保留英文，不要强行翻译。
- 每个结论必须给出文本依据。

## 脚本辅助

```bash
# Download LaTeX source + English PDF from arXiv
python3 scripts/fetch_paper.py <arxiv_url_or_id> <output_parent_dir>

# Convert PDF figures to PNG
python3 scripts/convert_figures.py <work_dir> <main_tex> --output-dir figures/png
```

## 收尾清理

最终润色报告生成后，删除过程中产生的过程性 `.md` 文件：`01-parse.md`、`02-insights.md`、`03-draft.md`、`03-research-notes.md`、`03.5-validation.md`、`04-critique.md`、`05-revision.md`。仅保留最终报告 `{YYYY-MM-DD}-{title}.md`、`figure_map.json`、源码目录 `source/` 与下载的 PDF。

## 参考库

- Type adaptation: [type-adaptation-rules.md](references/type-adaptation-rules.md)
- Figure interpretation: [figure-interpretation-guide.md](references/figure-interpretation-guide.md)
- Style guide: [style-guide.md](references/style-guide.md)
