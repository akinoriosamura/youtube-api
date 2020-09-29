import os
import time
import pandas as pd
from apiclient.discovery import build
from apiclient.errors import HttpError


API_KEY = os.environ['API_KEY2']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CHANNEL_IDs = ['UCmsA3A5_HKBwI9OktSttTFg', 'UCN559lrbV9wt46NwlnPJtPw']
CHANNEL_NAMEs = ['fukuse yuuriマリリン', '会社員J']

for (CHANNEL_ID, CHANNEL_NAME) in zip(CHANNEL_IDs, CHANNEL_NAMEs):
    P_NextPageToken = "nextPagetoken_" + CHANNEL_NAME + ".txt"

    searches = [] #videoidを格納する配列
    videos = [] #各動画情報を格納する配列
    if os.path.exists(P_NextPageToken):
        with open(P_NextPageToken) as f:
            _nextPagetoken = f.read()
            print(_nextPagetoken)
            if _nextPagetoken == 'None':
                nextPagetoken = None
            else:
                nextPagetoken = _nextPagetoken
    else:
        nextPagetoken = None
    nextpagetoken = None

    youtube = build(
        YOUTUBE_API_SERVICE_NAME, 
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
        )
    """
    part=\
        contentDetails,\
        statistics,\
        brandingSettings,\
        snippet,\
        id\
        &order=date&maxResults=1'
    """

    while True:
        if nextPagetoken != None:
            nextpagetoken = nextPagetoken

        try:
            search_response = youtube.search().list(
            part = "snippet",
            channelId = CHANNEL_ID,
            maxResults = 50,
            order = "date",
            pageToken = nextpagetoken
            ).execute()  
        except:
            print(" ================== ")
            print("maybe no quotes")
            print("Next nextPagetoken: ", nextPagetoken)
            print("next get information")
            break

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                searches.append(search_result["id"]["videoId"])
        try:
            nextPagetoken =  search_response["nextPageToken"]
            with open(P_NextPageToken, mode='w') as f:
                f.write(str(nextPagetoken))
            # break
        except:
            print(" ================== ")
            print("maybe no more nextPagetoken")
            print("next get information")
            with open(P_NextPageToken, mode='w') as f:
                f.write('finish')
            break

    print("num searche videos: ", len(searches))
    for result in searches:
        video_response = youtube.videos().list(
        part = 'snippet,statistics',
        id = result
        ).execute()

        for video_result in video_response.get("items", []):
            if video_result["kind"] == "youtube#video":
                des = video_result["snippet"]["description"].replace('\n','').replace('\r','')
                if 'viewCount' not in video_result["statistics"].keys():
                    print(" ================== ")
                    print("no view count in: ", video_result)
                    videos.append(
                        [
                            video_result["id"],
                            video_result["snippet"]["channelId"],
                            video_result["snippet"]["title"],
                            des,
                            '-1',
                            '-1',
                            '-1',
                            '-1',
                            '-1',
                            video_result["snippet"]["publishedAt"]
                        ]
                    )
                elif 'likeCount' not in video_result["statistics"].keys():
                    print(" ================== ")
                    print("no like count in: ", video_result)
                    videos.append(
                        [
                            video_result["id"],
                            video_result["snippet"]["channelId"],
                            video_result["snippet"]["title"],
                            des,
                            video_result["statistics"]["viewCount"],
                            '-1',
                            '-1',
                            '-1',
                            '-1',
                            video_result["snippet"]["publishedAt"]
                        ]
                    )
                elif 'commentCount' not in video_result["statistics"].keys():
                    print(" ================== ")
                    print("no comment count in: ", video_result)
                    videos.append(
                        [
                            video_result["id"],
                            video_result["snippet"]["channelId"],
                            video_result["snippet"]["title"],
                            des,
                            video_result["statistics"]["viewCount"],
                            video_result["statistics"]["likeCount"],
                            video_result["statistics"]["dislikeCount"],
                            video_result["statistics"]["favoriteCount"],
                            '-1',
                            video_result["snippet"]["publishedAt"]
                        ]
                    )
                else:
                    videos.append(
                        [
                            video_result["id"],
                            video_result["snippet"]["channelId"],
                            video_result["snippet"]["title"],
                            des,
                            video_result["statistics"]["viewCount"],
                            video_result["statistics"]["likeCount"],
                            video_result["statistics"]["dislikeCount"],
                            video_result["statistics"]["favoriteCount"],
                            video_result["statistics"]["commentCount"],
                            video_result["snippet"]["publishedAt"]
                        ]
                    )  

    videos_report = pd.DataFrame(videos, columns=['id', 'channelId', 'title', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount', 'publishedAt', 'description'])
    videos_report.to_csv(CHANNEL_NAME + ".csv", mode='a', index=None)
    print(" ============================ ")
    print(" finish create report of : ", CHANNEL_NAME)
    time.sleep(3)

print("================================")
print("finish all list ")