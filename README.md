# Skills

个人常用的 skill 汇总。每个子目录是一个独立 skill，遵循 `SKILL.md` + 可选 `scripts/`、`references/`、`examples/` 的结构，可直接复用或作为新 skill 的脚手架。

## 目录结构

```
skills/
└── <skill-name>/
    ├── SKILL.md          # skill 入口：frontmatter（name/description）+ 工作流与约束
    ├── manifest.json     # 可选：元数据
    ├── scripts/          # 可选：辅助脚本
    ├── references/       # 可选：分阶段参考资料 / 规则
    └── examples/         # 可选：示例输入输出
```

## 收录的 Skills

| Skill | 说明 | 触发方式 |
|-------|------|---------|
| [paper-deconstruct](./paper-deconstruct) | 面向工程复现与批判性思维的论文分析引擎，6 阶段流水线生成 13 章节技术解构报告 | 提供 arXiv URL/ID、PDF、LaTeX 目录或论文标题，或「读论文 / 论文解析 / 技术总结」 |

## 使用方式

1. 复制目标 skill 目录到你的 Claude Code skills 路径（如 `~/.claude/skills/`），或在仓库内直接使用。
2. 在对话中命中触发条件即可自动激活，也可用 `/<skill-name>` 显式调用。

## 新增 Skill

1. 新建 `<skill-name>/` 目录，按上面的结构组织。
2. 编写 `SKILL.md`：frontmatter 中的 `description` 需写清触发场景与关键词，正文写明输入输出契约、工作流、边界与约束。
3. 辅助脚本放 `scripts/`，分阶段规则放 `references/`，并在 `SKILL.md` 中以相对路径链接。
4. 在本 README 的「收录的 Skills」表格中登记一行。

> English version: [README.en.md](./README.en.md)
