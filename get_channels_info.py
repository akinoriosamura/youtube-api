import os
import time
import requests

import pandas as pd


API_KEY = os.environ['API_KEY']
CHANNEL_ID = 'UCCuizDTLsr-mNm_PEGdChVg'

base_url = 'https://www.googleapis.com/youtube/v3'
url = base_url + '/search?key=%s&channelId=%s&part=\
    contentDetails,\
    statistics,\
    brandingSettings,\
    snippet,\
    id\
    &order=date&maxResults=1'
infos = []

while True:
    time.sleep(3)
    response = requests.get(url % (API_KEY, CHANNEL_ID))
    if response.status_code != 200:
        print('エラーで終わり')
        print(response._content)
        import pdb;pdb.set_trace()
        break
    result = response.json()
    infos.extend([
        [item['id']['videoId'], item['snippet']['title'], item['snippet']['description'], item['snippet']['publishedAt']]
        for item in result['items'] if item['id']['kind'] == 'youtube#video'
    ])
    import pdb;pdb.set_trace()

    if 'nextPageToken' in result.keys():
        if 'pageToken' in url:
            url = url.split('&pageToken')[0]
        url += f'&pageToken={result["nextPageToken"]}'
    else:
        print('正常終了')
        break

videos = pd.DataFrame(infos, columns=['videoId', 'title', 'description', 'publishedAt'])
videos.to_csv('videos.csv', index=None)