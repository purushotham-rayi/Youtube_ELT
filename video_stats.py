import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY=os.getenv("API_KEY")
CHANNEL_HANDLE="MrBeast"
url=f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"


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
    
if __name__ == "__main__":
    print("get_playlist_id will be executed")
    print(get_playlist_id())
else:
    print("get_playlist_id will be executed")