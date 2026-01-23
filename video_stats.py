import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY=os.getenv("API_KEY")
CHANNEL_HANDLE="MrBeast"
url=f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
maxResults=50


def get_playlist_id():
    try:
        response=requests.get(url)
        data=response.json()

        response.raise_for_status()
        # json_data=json.dumps(data,indent=4)
        # print(json_data)

        channel_items=data["items"][0]
        channel_playlist_id=channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        # print(channel_playlist_id)
        return channel_playlist_id
    except requests.exceptions.RequestException as e:
        print(f"Error occured: {e}")
        raise e

def get_video_ids(playlist_ID):
    video_ids=[]
    pageToken = None
    base_url=f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_ID}&key={API_KEY}"
    try:
        while True:
            url=base_url
            if pageToken:
                url+=f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data=response.json()

            for item in data.get('items',[]):
                video_id=item['contentDetails']['videoId']
                video_ids.append(video_id)
            pageToken=data.get('nextPageToken')
            if not pageToken:
                break
    except requests.exceptions.RequestException as e:
        raise e
    return video_ids

playlist_ID = get_playlist_id()
if __name__ == "__main__":
    playlist_ID=get_playlist_id()
    get_video_ids(playlist_ID)