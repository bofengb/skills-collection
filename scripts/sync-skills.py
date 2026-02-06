#!/usr/bin/env python3
"""
Sync skills from public GitHub repos based on skills-manifest.yaml
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


def sync_directory(repo: str, branch: str, src_path: str, dest_path: Path) -> List[str]:
    """Sync a directory recursively. Returns list of updated files."""
    updated = []
    contents = fetch_directory_contents(repo, src_path, branch)

    if contents is None:
        return updated

    for item in contents:
        item_src = item["path"]
        item_name = item["name"]
        item_dest = dest_path / item_name

        if item["type"] == "file":
            if sync_file(repo, branch, item_src, item_dest):
                updated.append(str(item_dest))
        elif item["type"] == "dir":
            updated.extend(sync_directory(repo, branch, item_src, item_dest))

    return updated


def sync_skill(skill: dict) -> List[str]:
    """Sync a single skill entry. Returns list of updated files."""
    name = skill["name"]
    source = skill["source"]
    repo = source["repo"]
    branch = source.get("branch", "main")
    src_path = source["path"]
    dest_path = Path(skill["destination"])

    print(f"Syncing: {name} from {repo}")

    # Check if source is a directory (ends with /)
    if src_path.endswith("/"):
        return sync_directory(repo, branch, src_path.rstrip("/"), dest_path)
    else:
        if sync_file(repo, branch, src_path, dest_path):
            return [str(dest_path)]
        return []


def main():
    # Find manifest file
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    manifest_path = repo_root / "skills-manifest.yaml"

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
    updated_skills = []

    for skill in skills:
        updated = sync_skill(skill)
        if updated:
            all_updated.extend(updated)
            updated_skills.append(skill["name"])

    # Summary
    print()
    if all_updated:
        print(f"Updated {len(all_updated)} file(s):")
        for f in all_updated:
            print(f"  - {f}")

        # Output for GitHub Actions
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"updated=true\n")
                f.write(f"skills={', '.join(updated_skills)}\n")
    else:
        print("All skills are up to date")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("updated=false\n")


if __name__ == "__main__":
    main()
