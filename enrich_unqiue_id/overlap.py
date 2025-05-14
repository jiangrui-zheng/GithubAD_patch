import pandas as pd

# 读取两张 CSV
df_ghsa = pd.read_csv(
    '/home/jzheng36/code/traceability/enrich_unqiue_id/ghsa_no_commit_urls.csv'
)  # 包含 ghsa, cve, owner/repo
df_commit = pd.read_csv(
    '/home/jzheng36/code/traceability/enrich_unqiue_id/repo2unique_ids.csv'
)  # 包含 commit_sha, commit_message, unique_id, repo

df_ghsa = df_ghsa.rename(columns={'owner/repo': 'repo'})

# 取交集
df_overlap = pd.merge(
    df_ghsa,
    df_commit,
    on='repo',
    how='inner',
    suffixes=('_ghsa', '_commit')
)

output_path = '/home/jzheng36/code/traceability/enrich_unqiue_id/overlap_info.csv'
df_overlap.to_csv(output_path, index=False)
