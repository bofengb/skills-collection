# Skills Collection

> **Disclaimer:** This repository **does not contain original work**. All skills are automatically mirrored from their original public repositories. Full credit and ownership belong to the original authors listed below. This is simply a convenience collection for personal use.

A personal collection of Claude Code skills synced from public repositories via GitHub Actions.

## How It Works

- Skills are defined in `skills-manifest.yaml` (at the repo root)
- A GitHub Action runs manually to sync updates from upstream repos
- Skills are downloaded to this `skills/` directory

## Original Authors & Sources

**All credit belongs to the original authors.** This repository does not claim any ownership or credit for these skills. Each skill is the intellectual property of its respective creator.

| Skill | Source | Author |
|-------|--------|--------|
| brainstorming | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/brainstorming) | [obra](https://github.com/obra) |
| frontend-design | [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design) | [Anthropic](https://github.com/anthropics) |
| supabase-postgres-best-practices | [supabase/agent-skills](https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices) | [Supabase](https://github.com/supabase) |
| find-skills | [vercel-labs/skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) | [Vercel](https://github.com/vercel-labs) |
| database-schema-designer | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/main/skills/database-schema-designer) | [Softaworks](https://github.com/softaworks) |
| postgresql-design | [wshobson/agents](https://github.com/wshobson/agents/tree/main/plugins/database-design/skills/postgresql) | [wshobson](https://github.com/wshobson) |

## Adding Skills

Edit `skills-manifest.yaml` (at the repo root):

```yaml
skills:
  - name: skill-name
    source:
      repo: owner/repo
      branch: main
      path: path/to/skill/
    destination: skills/skill-name/
```

Then push to trigger the sync workflow.

## License & Attribution

**This repository contains no original content.** All skills are the property of their original authors and retain their original licenses from their source repositories.

- All intellectual property rights belong to the original authors
- Please refer to the source repositories linked above for licensing terms
- If you use any skill, credit should go to the original author, not this repository
