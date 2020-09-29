import os
import time
import traceback
import pandas as pd
from apiclient.discovery import build
from apiclient.errors import HttpError


API_KEY = os.environ['API_KEY10']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
NUM_TOTAL_VIDEOS = 0
with open('./channel_urls.txt') as f:
    _CHANNEL_URLs = f.readlines()
    CHANNEL_URLs = [ci.strip() for ci in _CHANNEL_URLs] 
with open('./channel_names.txt') as f:
    _CHANNEL_NAMEs = f.readlines()
    CHANNEL_NAMEs = [os.path.basename(cn.strip()) for cn in _CHANNEL_NAMEs] 
print("CHANNEL_URLs: ", CHANNEL_URLs)
print("CHANNEL_NAMEs: ", CHANNEL_NAMEs)
assert len(CHANNEL_URLs) == len(CHANNEL_NAMEs), "no match length ids and names"
assert len(set(CHANNEL_URLs)) == len(set(CHANNEL_NAMEs)), "there is not unique itrems"

for (CHANNEL_URL, CHANNEL_NAME) in zip(CHANNEL_URLs, CHANNEL_NAMEs):
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
    # get channelid
    if 'channel' in CHANNEL_URL:
        CHANNEL_ID = os.path.basename(CHANNEL_URL)
    else:
        search_response = youtube.channels().list(
        part = "snippet",
        forUsername = os.path.basename(CHANNEL_URL),
        maxResults = 1
        ).execute()
        CHANNEL_ID = search_response.get("items", [])[0]['id']
    print("CHANNEL_ID: ", CHANNEL_ID)
    #import pdb;pdb.set_trace()
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
            print("please try first of :", CHANNEL_NAME)
            traceback.print_exc()
            exit()

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                searches.append(search_result["id"]["videoId"])
        try:
            nextPagetoken =  search_response["nextPageToken"]
            # with open(P_NextPageToken, mode='w') as f:
            #     f.write(str(nextPagetoken))
            # break
        except:
            print(" ================== ")
            print("maybe no more nextPagetoken")
            print("next get information")
            # with open(P_NextPageToken, mode='w') as f:
            #     f.write('finish')
            traceback.print_exc()
            break

    print("num searche videos: ", len(searches))
    NUM_TOTAL_VIDEOS += len(searches)
    for result in searches:
        try:
            video_response = youtube.videos().list(
            part = 'snippet,statistics',
            id = result
            ).execute()
        except:
            print(" ================== ")
            print("please try first of :", CHANNEL_NAME)
            traceback.print_exc()
            exit()

        for video_result in video_response.get("items", []):
            if video_result["kind"] == "youtube#video":
                des = video_result["snippet"]["description"].replace('\n','').replace('\r','')
                if 'viewCount' not in video_result["statistics"].keys():
                    # print(" ================== ")
                    # print("no view count in: ", video_result)
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
                    # print(" ================== ")
                    # print("no like count in: ", video_result)
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
                    # print(" ================== ")
                    # print("no comment count in: ", video_result)
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

    videos_report = pd.DataFrame(videos, columns=['id', 'channelId', 'title', 'description', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount', 'publishedAt'])
    videos_report.to_csv(CHANNEL_NAME + ".csv", mode='a', index=None)
    print(" ============================ ")
    print(" finish create report of : ", CHANNEL_NAME)
    time.sleep(3)

print("================================")
print("finish all list ")
print(" total num: ", NUM_TOTAL_VIDEOS)