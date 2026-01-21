import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./env")

API_KEY=os.getenv("API_KEY")
CHANNEL_HANDLE="MrBeast"
url=f"https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

def get_playlist_id():
    print("Funtion Started.............")
    try:
        print("Making API Requests......")
        response=requests.get(url)
        print(f"Response Status: {response.status_code}")

        data=response.json()
        print('JSON parsed Successfully................')

        json_data=json.dumps(data,indent=4)
        print(json_data)

        # with open('video_stats.json','w') as f:
        #     f.write(json_data)

        channel_items=data['items'][0]
        # channel_playlistId=channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_items)
        return channel_items
    except requests.exceptions.RequestException as e:
        print(f"Error occured: {e}")
        raise e
    
if __name__ == "__main__":
    print("Starting Program..................")
    get_playlist_id()
    print("...........................\n Program finished")