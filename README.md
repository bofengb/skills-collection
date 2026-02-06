# Skills Collection

A personal collection of Claude Code skills synced from public repositories via GitHub Actions.

## How It Works

- Skills are defined in `skills-manifest.yaml`
- A GitHub Action runs manually to sync updates from upstream repos
- Skills are downloaded to `skills/` directory

## Skill Sources & Credits

All skills in this collection are sourced from their original authors. This repo does not claim ownership of any skills.

| Skill | Source | Author |
|-------|--------|--------|
| brainstorming | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/brainstorming) | [obra](https://github.com/obra) |
| frontend-design | [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design) | [Anthropic](https://github.com/anthropics) |
| supabase-postgres-best-practices | [supabase/agent-skills](https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices) | [Supabase](https://github.com/supabase) |
| find-skills | [vercel-labs/skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) | [Vercel](https://github.com/vercel-labs) |
| database-schema-designer | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/main/skills/database-schema-designer) | [Softaworks](https://github.com/softaworks) |

## Adding Skills

Edit `skills-manifest.yaml`:

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

## License

Each skill retains its original license from its source repository. Please refer to the original repos for license information.
