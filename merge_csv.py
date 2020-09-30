import os
import time
import pandas as pd

target_dir = "../..//Downloads/cosme_youtuber"
csv_files = os.listdir(target_dir)

df_merged = None
columns = ['id', 'channelId', 'title', 'description', 'viewCount', 'likeCount', 'dislikeCount','favoriteCount', 'commentCount', 'publishedAt']
for id_f, csv_f in enumerate(csv_files):
    if '.csv' in csv_f:
        print(csv_f)
        _df = pd.read_csv(os.path.join(target_dir, csv_f))
        _df.columns = columns
        print(_df.shape)
        if id_f == 0:
            df_merged = _df
        else:
            df_merged = pd.concat([df_merged, _df])
        print(df_merged.shape)
import pdb;pdb.set_trace()
df_merged.to_csv("merged_cosme_youtuber.csv", mode='a', index=None)

