# Skills (English)

A personal collection of commonly used skills. Each subdirectory is a standalone skill following the `SKILL.md` + optional `scripts/`, `references/`, `examples/` layout — ready to reuse or to use as scaffolding for new skills.

## Directory Layout

```
skills/
└── <skill-name>/
    ├── SKILL.md          # skill entry: frontmatter (name/description) + workflow & constraints
    ├── manifest.json     # optional: metadata
    ├── scripts/          # optional: helper scripts
    ├── references/       # optional: per-stage references / rules
    └── examples/         # optional: example inputs/outputs
```

## Available Skills

| Skill | Description | Trigger |
|-------|-------------|---------|
| [paper-deconstruct](./paper-deconstruct) | Engineering-first, critical-thinking paper analysis engine; a 6-stage pipeline producing a 13-section technical deconstruction report | Provide an arXiv URL/ID, PDF, LaTeX directory, or paper title, or say "read paper / analyze paper / 论文解析" |

## Usage

1. Copy the target skill directory into your Claude Code skills path (e.g. `~/.claude/skills/`), or use it in place within this repo.
2. It auto-activates when trigger conditions are met, or invoke it explicitly with `/<skill-name>`.

## Adding a New Skill

1. Create a `<skill-name>/` directory following the layout above.
2. Write `SKILL.md`: the `description` in frontmatter should clearly state trigger scenarios and keywords; the body should cover the input/output contract, workflow, boundaries, and constraints.
3. Put helper scripts in `scripts/`, per-stage rules in `references/`, and link them via relative paths in `SKILL.md`.
4. Register a row in the "Available Skills" table above.
