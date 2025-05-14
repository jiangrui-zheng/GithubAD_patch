import os
import subprocess
import csv
import re
from multiprocessing import Pool, cpu_count, Manager


input_file = '../data_collect/githubad_patch.csv'
repo_base_path = '../repos'
commit_logs_path = '../commit_logs'
output_dir = '../repo_commit_histories'

os.makedirs(repo_base_path, exist_ok=True)
os.makedirs(commit_logs_path, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# 正则表达式匹配 unique_id
unique_id_pattern = re.compile(r'[A-Z]{2,}-\d+')

# 克隆或更新仓库
def clone_or_pull_repo(repo):
    repo_name = repo.replace("/", "_")
    repo_path = os.path.join(repo_base_path, repo_name + ".git")
    if not os.path.exists(repo_path):
        print(f"Cloning {repo} as a bare repository...")
        subprocess.run(
            ["git", "clone", f"https://github.com/{repo}.git", repo_path],
            check=True
        )
    else:
        print(f"Fetching latest changes for {repo}...")
        subprocess.run(["git", "-C", repo_path, "fetch", "--all"], check=True)
    return repo_path


# 提取提交历史到日志文件
def save_commit_logs_to_file(repo_path, log_file):
    if os.path.exists(log_file):
        print(f"Log file for {repo_path} already exists. Skipping...")
        return
    print(f"Saving commit logs for {repo_path} to {log_file}...")
    with open(log_file, 'w') as f:
        subprocess.run(
            ["git", "-C", repo_path, "log", "--pretty=format:%H||%s"],
            stdout=f,
            text=True,
            check=True
        )

# 从日志文件中加载提交历史
def load_commit_logs_from_file(log_file):
    print(f"Loading commit logs from {log_file}...")
    with open(log_file, 'r', errors='replace') as f:
        commits = f.readlines()
    processed_commits = []
    for commit in commits:
        commit = commit.strip()
        if not commit or "||" not in commit:  # 跳过空行或没有分隔符的行
            print(f"Skipping invalid line: {commit}")
            continue
        sha, message = commit.split("||", 1)
        match = unique_id_pattern.search(message)
        unique_id = match.group(0) if match else "None"
        processed_commits.append({"commit_sha": sha, "commit_message": message, "unique_id": unique_id})
    return processed_commits

# 写入提交历史到 CSV 文件
def write_commits_to_csv(repo, commits):
    output_file = os.path.join(output_dir, f"{repo.replace('/', '_')}_commits.csv")
    with open(output_file, 'w', newline='') as out_f:
        writer = csv.DictWriter(out_f, fieldnames=["commit_sha", "commit_message", "unique_id"])
        writer.writeheader()
        writer.writerows(commits)
    print(f"Commits written to {output_file}")


def process_repo_entry(row):
    raw_repo = row['repo']
    repo = raw_repo.replace('_', '/')
    try:
        repo_path = clone_or_pull_repo(repo)
        log_file = save_commit_logs_to_file(repo_path, raw_repo)
        commits = load_commit_logs_from_file(log_file)
        write_commits_to_csv(raw_repo, commits)
    except subprocess.CalledProcessError as e:
        print(f"[{raw_repo}] Git error: {e}")
    except Exception as e:
        print(f"[{raw_repo}] Processing error: {e}")
    finally:
        # 清理裸仓库
        try:
            subprocess.run(["rm", "-rf", repo_path], check=True)
        except Exception:
            pass

if __name__ == "__main__":
    # 读取所有唯一的 repo 条目
    entries = []
    seen = set()
    with open(input_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_repo = row['repo']
            if raw_repo in seen:
                continue
            seen.add(raw_repo)
            entries.append(row)

    # 并行处理
    pool_size = min(cpu_count(), len(entries))
    with Pool(pool_size) as pool:
        pool.map(process_repo_entry, entries)

    print("All unique repositories processed.")