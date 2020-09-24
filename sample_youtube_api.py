from apiclient.discovery import build
import pandas as pd

def get_video_info(part, q, order, type, num):
    dic_list = []
    search_response = youtube.search().list(part=part,q=q,order=order,type=type)
    output = youtube.search().list(part=part,q=q,order=order,type=type).execute()

    #一度に5件しか取得できないため何度も繰り返して実行
    for i in range(num):        
        dic_list = dic_list + output['items']
        search_response = youtube.search().list_next(search_response, output)
        output = search_response.execute()

    df = pd.DataFrame(dic_list)
    #各動画毎に一意のvideoIdを取得
    df1 = pd.DataFrame(list(df['id']))['videoId']
    #各動画毎に一意のvideoIdを取得必要な動画情報だけ取得
    df2 = pd.DataFrame(list(df['snippet']))[['channelTitle','publishedAt','channelId','title','description']]
    ddf = pd.concat([df1,df2], axis = 1)

    return ddf

#videoIdを入力することで、その動画の具体的な再生回数やいいね数を取得する関数を作成
def get_statistics(id):
    statistics = youtube.videos().list(part = 'statistics', id = id).execute()['items'][0]['statistics']
    return statistics

if __name__ == "__main__":
    YOUTUBE_API_KEY = 'XXX'

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    """
    search_response = youtube.search().list(
    part='snippet',
    #検索したい文字列を指定
    q='ボードゲーム',
    #視聴回数が多い順に取得
    order='viewCount',
    type='video',
    ).execute()
    print(search_response['items'][0])
    """

    ddf = get_video_info(part='snippet',q='ボードゲーム',order='viewCount',type='video',num = 20)
    print(ddf)

    df_static = pd.DataFrame(list(df['videoId'].apply(lambda x : get_statistics(x))))
    df_output = pd.concat([df,df_static], axis = 1)
    print(df_output)