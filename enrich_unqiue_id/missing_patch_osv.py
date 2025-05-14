import os
import json
import csv
from urllib.parse import urlparse

# 根目录，请根据需要调整
ROOT_DIR = '/home/jzheng36/code/osv_data'
OUTPUT_CSV = 'ghsa_no_commit_urls.csv'

def extract_owner_repo(url):
    """
    从 URL 提取 owner/repo；
    例如：https://github.com/owner/repo/commit/...
    -> 返回 "owner/repo"
    """
    if 'github.com' not in url:
        return ''
    path = urlparse(url).path  # "/owner/repo/..."
    parts = [p for p in path.split('/') if p]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return ''

with open(OUTPUT_CSV, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['ghsa', 'cve', 'owner/repo', 'missing_patch'])
    writer.writeheader()

    # 遍历各子文件夹
    for subdir, _, files in os.walk(ROOT_DIR):
        for fname in files:
            if not fname.startswith('GHSA-') or not fname.endswith('.json'):
                continue

            full_path = os.path.join(subdir, fname)
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ghsa_id = data.get('id', fname[:-5])  # 以 JSON 中 id 字段为准，否则用文件名
            cves = data.get('aliases', [])
            # 筛选 URL 列表中不包含 "commit" 的 URL
            urls = data.get('references', [])
            # 有些 JSON 结构可能是：
            # "references": [{"type": "...", "url": "..."}, ...]
            # 或者直接是 URL 字符串列表，需要兼容
            raw_urls = []
            for ref in urls:
                if isinstance(ref, dict):
                    raw_urls.append(ref.get('url', ''))
                elif isinstance(ref, str):
                    raw_urls.append(ref)
            # 过滤
            label = 1
            # 筛选出包含 "github" 的 URL
            github_urls = [u for u in raw_urls if 'github.com' in u]
            if not github_urls:
                # 如果没有 GitHub URL，跳过
                continue
            
            first_url = github_urls[0]
            owner_repo = extract_owner_repo(first_url)

            # 筛选出不包含 "commit" 的 GitHub URL
            no_commit_urls = [u for u in github_urls if 'commit' not in u]
            if not no_commit_urls:
                label = 0 # 没有 "commit" 的 URL, missing patch
            else:
                label = 1 # 有 "commit" 的 URL
            

            writer.writerow({
                'ghsa': ghsa_id,
                'cve': ';'.join(cves),
                'owner/repo': owner_repo,
                'missing_patch': label
            })

print(f"已生成 CSV：{OUTPUT_CSV}")
