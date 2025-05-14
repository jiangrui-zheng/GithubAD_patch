import json
import requests
import os
from pathlib import Path
import time

eco2cve2reference = {}
home_dir = os.path.expanduser("~")
github_token = json.load(open(home_dir + "/secret.json", "r"))["github"]

def can_clone_github_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"Bearer {github_token}"}
    try:
        response = requests.get(url, headers=headers)
        time.sleep(1)
        if response.status_code == 200:
            data = response.json()
            return data.get("private") is False  # 如果是公有仓库，则可以克隆
        print("return status wrong")
        return False
    except requests.exceptions.RequestException:
        return False

linecount = 0
for json_file in list(Path('../../advisory-database/advisories/github-reviewed/').rglob('*.json')):
    if linecount % 100 == 0:
        print(linecount)
    linecount += 1
    entry = json.load(open(json_file, "r"))
    if len(entry["aliases"]) == 0:
        continue
    cve = entry["aliases"][0]
    affected = entry["affected"]
    references = entry["references"]
    for each_affected in affected:
        ecosystem = each_affected["package"]["ecosystem"]
        name = each_affected["package"]["name"]
        if "/" in name and len(name.split("/")) == 2:
            if can_clone_github_repo(name.split("/")[0], name.split("/")[1]):
                eco2cve2reference.setdefault(ecosystem, {})
                eco2cve2reference[ecosystem].setdefault(cve, [])
                eco2cve2reference[ecosystem][cve].append("https://github.com/" + name + "/commit/xxx")
        if ecosystem not in ["Maven", "PyPI", "npm", "Go", "Composor"]: continue
        eco2cve2reference.setdefault(ecosystem, {})
        eco2cve2reference[ecosystem].setdefault(cve, [])
        for ref in references:
            eco2cve2reference[ecosystem][cve].append(ref["url"])

json.dump(eco2cve2reference, open("../../advisory-database/eco2cve2reference.json", "w"))
