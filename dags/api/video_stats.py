# This part is for when the title has special characters and the console is unable to parse.
import sys
import io

# Setting the UTF-8 encoding for Windows console
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Regular program starts from here
import requests
import json
import os
from dotenv import load_dotenv

#For saving the filename using the date
from datetime import datetime
import pendulum

#For airflow related operations
from airflow.decorators import task
from airflow.models import Variable

# For getting environment variables
load_dotenv(dotenv_path=".env")

API_KEY=Variable.get("API_KEY")
CHANNEL_HANDLE=Variable.get("CHANNEL_HANDLE")

# The below two lines can be used when running directly with python. But we will be using airflow env variables. So we comment these.
# API_KEY=os.getenv("API_KEY")
# CHANNEL_HANDLE="MrBeast"
url=f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
maxResults=50

@task
# Get the playlist ids from the channel
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

@task
# Get the individual video ids from the playlist
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

@task
# Getting the video data for each video
def extract_video_data(video_ids):
    extracted_data=[]

    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list),batch_size):
            yield video_id_list[video_id: video_id+batch_size]

    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str=",".join(batch)
            url=f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data=response.json()
            for item in data.get('items',[]):
                video_id=item['id']
                snippet=item['snippet']
                contentDetails=item['contentDetails']
                statistics=item['statistics']
            
                video_data={
                    "video_id":video_id,
                    "title":snippet['title'],
                    "publishedAt":snippet['publishedAt'],
                    "duration":contentDetails['duration'],
                    "viewCount":statistics.get('viewCount', None),
                    "likeCount":statistics.get('likeCount',None),
                    "commentCount":statistics.get('commentCount', None)
                }
                extracted_data.append(video_data)
        return extracted_data
    
    except requests.exceptions.RequestException as e:
        raise e

@task
# Save the extracted data to JSON file.    
def save_to_json(extracted_data):
    # timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # The above line is useful if we are running directly in python. But with airflow it will default to UTC.  
    timestamp=pendulum.now("America/Chicago").strftime("%Y-%m-%d_%H-%M-%S")
    file_path=f"./data/YT_data_{timestamp}.json"

    with open(file_path,"w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    playlist_ID=get_playlist_id()
    video_ids=get_video_ids(playlist_ID)
    video_data=extract_video_data(video_ids)
    save_to_json(video_data)