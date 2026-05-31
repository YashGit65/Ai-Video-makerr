import os
import googleapiclient.http
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'token.json'

def authenticate_youtube():
    creds = None

    # Load saved token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    # Login only if needed
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret_252891285056-agr50dpkn4glfepbgsjdrf5q4rnou0pc.apps.googleusercontent.com.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    youtube = build(
        "youtube",
        "v3",
        credentials=creds
    )

    return youtube

def upload_video(youtube,topic,script,video_file):
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": topic,
            "description": script,
            "tags": ["#shorts","#youtubeshorts","#Viral","#Trending","#ytshorts","#Shorts","#YouTubeShorts","#ShortsVideo"]
        },
        "status":{
            "privacyStatus": "public"
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

        print(f"Video uploaded with ID: {response['id']}")

if __name__ == "__main__":
    youtube = authenticate_youtube()
    upload_video(youtube)

