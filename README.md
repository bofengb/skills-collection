# AI Toolkit

A personal collection of AI-related resources — skills, links, prompts, and more.

## What's Inside

| Folder | Description |
|--------|-------------|
| [skills/](skills/) | Claude Code skills synced from public repos via GitHub Actions |
| [links/](links/) | Curated collection of useful AI links and resources |
| [prompts/](prompts/) | Reusable prompts and prompt templates |

## Skills Sync

Skills are automatically mirrored from upstream public repositories. See [skills/README.md](skills/README.md) for the full list of sources and credits.

### Via GitHub Actions

Trigger the sync workflow from the [Actions tab](../../actions/workflows/sync-skills.yml) via `workflow_dispatch`. The action commits and pushes any changes automatically, and shows a summary of what changed.

### Locally

```bash
# One-time setup
pip install pyyaml

# Sync skills from upstream
python scripts/sync-skills.py

# Review and push changes
git diff skills/
git add skills/
git commit -m "Update skills: <list changed skills>"
git push
```
