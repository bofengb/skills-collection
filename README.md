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

To sync skills manually:
```bash
pip install pyyaml
python scripts/sync-skills.py
```

Or trigger the GitHub Action via `workflow_dispatch`.
