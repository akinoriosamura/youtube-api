import os
import time
import traceback
import pandas as pd
from apiclient.discovery import build
from apiclient.errors import HttpError


API_KEY = os.environ['API_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
NUM_TOTAL_COMMENTZS = 0
VIDEO_ID = 'GBDFkokhh-Q'

comments = []
nextPagetoken = None
nextpagetoken = None

youtube = build(
    YOUTUBE_API_SERVICE_NAME, 
    YOUTUBE_API_VERSION,
    developerKey=API_KEY
    )

# get comment ids by video id
while True:
    if nextPagetoken != None:
        nextpagetoken = nextPagetoken

    try:
        search_response = youtube.commentThreads().list(
        part = "id,snippet,replies",
        videoId	 = VIDEO_ID,
        maxResults = 100,
        order = "time",
        pageToken = nextpagetoken
        ).execute()  
    except:
        print(" ================== ")
        traceback.print_exc()
        exit()

    for search_result in search_response["items"]:
        if search_result["kind"] == "youtube#commentThread":
            # get [
            # topcomment.id, 
            # parent comment id,
            # videoid, 
            # topcomment.textDisplay,
            # topcomment.authorchannelid.value, 
            # topcomment.likeCount,
            # topcomment.publishedAt
            # ]
            if 'replies' in search_result.keys():
                comments.append(
                    [
                        search_result["snippet"]["topLevelComment"]["id"],
                        search_result["id"],
                        search_result["snippet"]["videoId"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                    ]
                )
                NUM_TOTAL_COMMENTZS += 1
                for reply_comment in search_result['replies']['comments']:
                    comments.append(
                        [
                            reply_comment["id"],
                            reply_comment["snippet"]["parentId"],
                            reply_comment["snippet"]["videoId"],
                            reply_comment["snippet"]["textDisplay"],
                            reply_comment["snippet"]["authorChannelId"]["value"],
                            reply_comment["snippet"]["likeCount"],
                            reply_comment["snippet"]["publishedAt"]
                        ]
                    )
                    NUM_TOTAL_COMMENTZS += 1
            else:
                comments.append(
                    [
                        search_result["snippet"]["topLevelComment"]["id"],
                        search_result["id"],
                        search_result["snippet"]["videoId"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                        search_result["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                    ]
                )
                NUM_TOTAL_COMMENTZS += 1
    try:
        nextPagetoken =  search_response["nextPageToken"]
    except:
        print(" ================== ")
        print("maybe no more nextPagetoken")
        print("next get information")
        # with open(P_NextPageToken, mode='w') as f:
        #     f.write('finish')
        traceback.print_exc()
        break


videos_report = pd.DataFrame(comments, columns=['commentId', 'threadId', 'video_id', 'textDisplay', 'authorChannelId', 'likeCount', 'publishedAt'])
videos_report.to_csv(VIDEO_ID + "_comments.csv", mode='a', index=None)
print(" ============================ ")
print(" finish create report of : ", VIDEO_ID)
time.sleep(3)

print("================================")
print("finish all list ")
print(" total num: ", NUM_TOTAL_COMMENTZS)