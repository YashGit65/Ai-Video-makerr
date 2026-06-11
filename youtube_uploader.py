import os
import googleapiclient.http
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'token.json'

# AGAR KABHI SAHI KARNO HO CODE TOH CLIENT.JSON WALI FILE ADD KRKE KRNA OR YT VIDEO DHEK LENA IS CODE KE LIYE

def authenticate_youtube(file):

    flow = InstalledAppFlow.from_client_secrets_file(
        file,
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    return build(
        "youtube",
        "v3",
        credentials=creds
    )

def upload_video(youtube, topic, script, video_file, privacy_status="public"):
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": topic,
            "description": script,
            "tags": ["#shorts","#youtubeshorts","#Viral","#Trending","#ytshorts","#Shorts","#YouTubeShorts","#ShortsVideo"]
        },
        "status":{
            "privacyStatus": privacy_status
        }
    }

    # put the path of the video that you want to upload
    media_file = video_file

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=googleapiclient.http.MediaFileUpload(media_file, chunksize=-1, resumable=True)
    )

    response = None 

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress()*100)}%")

    video_id = response["id"]
    print(f"Video uploaded with ID: {video_id}")
    return video_id

if __name__ == "__main__":
    youtube = authenticate_youtube()
    upload_video(youtube)

