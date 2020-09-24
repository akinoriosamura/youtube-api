import os
import pandas as pd
from apiclient.discovery import build
from apiclient.errors import HttpError


API_KEY = os.environ['API_KEY2']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CHANNEL_ID = 'UCCuizDTLsr-mNm_PEGdChVg'

channels = [] #チャンネル情報を格納する配列
searches = [] #videoidを格納する配列
videos = [] #各動画情報を格納する配列
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

    search_response = youtube.search().list(
      part = "snippet",
      channelId = CHANNEL_ID,
      maxResults = 2,
      order = "date",
      pageToken = nextpagetoken
      ).execute()  

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            searches.append(search_result["id"]["videoId"])

    try:
        nextPagetoken =  search_response["nextPageToken"]
    except:
        break
   
for result in searches:
    video_response = youtube.videos().list(
      part = 'snippet,statistics',
      id = result
      ).execute()

    for video_result in video_response.get("items", []):
        if video_result["kind"] == "youtube#video":
            videos.append([video_result["snippet"]["title"],video_result["statistics"]["viewCount"],video_result["statistics"]["likeCount"],video_result["statistics"]["dislikeCount"],video_result["statistics"]["commentCount"],video_result["snippet"]["publishedAt"]])  

videos_report = pd.DataFrame(videos, columns=['title', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'publishedAt'])
videos_report.to_csv("videos_report.csv", index=None)

channel_report = pd.DataFrame(channels, columns=['title', 'subscriberCount', 'videoCount', 'publishedAt'])
channel_report.to_csv("channels_report.csv", index=None)