import os
import pandas as pd

output_dir = '../repo_commit_histories'
combined_csv_path = 'repo2unique_ids.csv'

combined_data = []

for file_name in os.listdir(output_dir):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(output_dir, file_name)
        repo_name = file_name.replace('_commits.csv', '').replace('_', '/')
        
        df = pd.read_csv(file_path)
        df['repo'] = repo_name
        df_filtered = df = df[~df['unique_id'].isna()]
        df['unique_id'] = df['unique_id'].astype(str)
        df = df[df['unique_id'].str.lower() != 'None']
        # 去除 unique_id 列中包含 "CVE", "GHSA", "UTF" 的行
        # df = df[~df['unique_id'].str.contains(r'CVE|GHSA|UTF', na=False)]
        combined_data.append(df_filtered)


combined_df = pd.concat(combined_data, ignore_index=True)
combined_df.to_csv(combined_csv_path, index=False)

combined_csv_path
