#!/usr/bin/env python3
"""
Sync skills from public GitHub repos based on skills/skills-manifest.yaml
"""

import os
import sys
import yaml
import urllib.request
import urllib.error
import json
from pathlib import Path
from typing import Optional, List, Dict


def get_raw_url(repo: str, branch: str, path: str) -> str:
    """Get raw GitHub content URL."""
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"


def get_api_url(repo: str, path: str, branch: str) -> str:
    """Get GitHub API URL for directory contents."""
    return f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"


def download_file(url: str) -> Optional[bytes]:
    """Download a file from URL."""
    try:
        req = urllib.request.Request(url)
        # Add GitHub token if available (for rate limiting)
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            req.add_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        print(f"  Error downloading {url}: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"  Error downloading {url}: {e.reason}")
        return None


def fetch_directory_contents(repo: str, path: str, branch: str) -> Optional[List[Dict]]:
    """Fetch directory listing from GitHub API."""
    url = get_api_url(repo, path.rstrip("/"), branch)
    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            req.add_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"  Error fetching directory {url}: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"  Error fetching directory {url}: {e.reason}")
        return None


def sync_file(repo: str, branch: str, src_path: str, dest_path: Path) -> bool:
    """Sync a single file. Returns True if file was updated."""
    url = get_raw_url(repo, branch, src_path)
    content = download_file(url)

    if content is None:
        return False

    # Check if file exists and has same content
    if dest_path.exists():
        existing = dest_path.read_bytes()
        if existing == content:
            return False

    # Write new content
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(content)
    return True


def sync_directory(repo: str, branch: str, src_path: str, dest_path: Path) -> tuple:
    """Sync a directory recursively. Returns (list of updated files, set of all synced dest paths)."""
    updated = []
    synced_paths = set()
    contents = fetch_directory_contents(repo, src_path, branch)

    if contents is None:
        return updated, synced_paths

    for item in contents:
        item_src = item["path"]
        item_name = item["name"]
        item_dest = dest_path / item_name

        if item["type"] == "file":
            synced_paths.add(item_dest)
            if sync_file(repo, branch, item_src, item_dest):
                updated.append(str(item_dest))
        elif item["type"] == "dir":
            sub_updated, sub_synced = sync_directory(repo, branch, item_src, item_dest)
            updated.extend(sub_updated)
            synced_paths.update(sub_synced)

    return updated, synced_paths


def remove_stale_files(dest_path: Path, synced_paths: set) -> List[str]:
    """Remove files in dest_path that are not in synced_paths. Returns list of removed files."""
    removed = []
    if not dest_path.exists():
        return removed
    for existing_file in sorted(dest_path.rglob("*")):
        if existing_file.is_file() and existing_file not in synced_paths:
            existing_file.unlink()
            removed.append(str(existing_file))
            print(f"  Removed stale file: {existing_file}")
    # Clean up empty directories
    for dirpath in sorted(dest_path.rglob("*"), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            dirpath.rmdir()
    return removed


def sync_skill(skill: dict) -> Dict:
    """Sync a single skill entry. Returns dict with 'updated' and 'removed' file lists."""
    name = skill["name"]
    source = skill["source"]
    repo = source["repo"]
    branch = source.get("branch", "main")
    src_path = source["path"]
    dest_path = Path(skill["destination"])

    print(f"Syncing: {name} from {repo}")

    # Check if source is a directory (ends with /)
    if src_path.endswith("/"):
        updated, synced_paths = sync_directory(repo, branch, src_path.rstrip("/"), dest_path)
        removed = remove_stale_files(dest_path, synced_paths)
    else:
        if sync_file(repo, branch, src_path, dest_path):
            updated = [str(dest_path)]
        else:
            updated = []
        removed = []

    return {"updated": updated, "removed": removed}


def main():
    # Find manifest file
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    manifest_path = repo_root / "skills" / "skills-manifest.yaml"

    if not manifest_path.exists():
        print(f"Error: {manifest_path} not found")
        sys.exit(1)

    # Change to repo root for relative paths
    os.chdir(repo_root)

    # Load manifest
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    skills = manifest.get("skills") or []
    if not skills:
        print("No skills configured in manifest")
        sys.exit(0)

    # Sync all skills
    all_updated = []
    all_removed = []
    changed_skills = []

    for skill in skills:
        result = sync_skill(skill)
        if result["updated"] or result["removed"]:
            all_updated.extend(result["updated"])
            all_removed.extend(result["removed"])
            changed_skills.append(skill["name"])

    # Summary
    print()
    has_changes = bool(all_updated or all_removed)

    if has_changes:
        if all_updated:
            print(f"Updated {len(all_updated)} file(s):")
            for f in all_updated:
                print(f"  + {f}")
        if all_removed:
            print(f"Removed {len(all_removed)} file(s):")
            for f in all_removed:
                print(f"  - {f}")
    else:
        print("All skills are up to date")

    # Output for GitHub Actions
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write(f"updated={'true' if has_changes else 'false'}\n")
            fh.write(f"skills={', '.join(changed_skills)}\n")

    # Output for GitHub Actions job summary
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write("## Skills Sync Summary\n\n")
            if has_changes:
                fh.write(f"**Skills changed:** {', '.join(changed_skills)}\n\n")
                if all_updated:
                    fh.write(f"### Updated ({len(all_updated)} files)\n\n")
                    for f in all_updated:
                        fh.write(f"- `{f}`\n")
                    fh.write("\n")
                if all_removed:
                    fh.write(f"### Removed ({len(all_removed)} files)\n\n")
                    for f in all_removed:
                        fh.write(f"- `{f}`\n")
                    fh.write("\n")
            else:
                fh.write("All skills are up to date. No changes detected.\n")


if __name__ == "__main__":
    main()
