import pandas as pd

# 加载 CSV 文件
df = pd.read_csv('/home/jzheng36/code/traceability/data_collect/githubad_patch.csv', on_bad_lines='skip')

# 提取唯一的 repo 值并统计
unique_repos = df['repo'].nunique()
print(f"Unique repos: {unique_repos}")
