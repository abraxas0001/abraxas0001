#!/usr/bin/env python3
import os
import re
import sys
import requests

# Determine owner from GITHUB_REPOSITORY (owner/repo)
repo = os.getenv("GITHUB_REPOSITORY", "")
if "/" not in repo:
    print("GITHUB_REPOSITORY not set or malformed:", repo)
    sys.exit(1)
owner = repo.split("/")[0]

# Use PERSONAL_TOKEN if available, otherwise GITHUB_TOKEN
token = os.getenv("PERSONAL_TOKEN") or os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github+json"}
if token:
    headers["Authorization"] = f"Bearer {token}"

try:
    resp = requests.get(f"https://api.github.com/users/{owner}", headers=headers, timeout=15)
except Exception as e:
    print("Network or request error:", e)
    sys.exit(1)

if resp.status_code != 200:
    print("Failed to fetch user info:", resp.status_code, resp.text)
    sys.exit(1)

followers = resp.json().get("followers", 0)

start = "<!-- followers-badge-start -->"
end = "<!-- followers-badge-end -->"
readme_path = "README.md"

try:
    with open(readme_path, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print("README.md not found in repository root.")
    sys.exit(1)

new_block = f"{start}\n[Follow on GitHub](https://github.com/{owner}) • Followers: **{followers}**\n{end}"

if start in text and end in text:
    pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.S)
    new_text = pattern.sub(new_block, text)
else:
    new_text = text.rstrip() + "\n\n" + new_block + "\n"

if new_text != text:
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("README updated to", followers, "followers")
else:
    print("No change needed (followers still {})".format(followers))
