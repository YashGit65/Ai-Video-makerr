import importlib
import os
import sys
from pathlib import Path

import streamlit as st

from youtube_uploader import authenticate_youtube, upload_video


# =====================================================
# Helpers
# =====================================================

def resolve_hf_api_token(user_token):
    token = (user_token or "").strip()

    if token:
        os.environ["api2"] = token
        os.environ["HF_TOKEN"] = token
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = token
    else:
        for env_name in (
            "api2",
            "HF_TOKEN",
            "HUGGINGFACEHUB_API_TOKEN",
        ):
            os.environ.pop(env_name, None)

    return token


def load_generator(api_token):
    resolve_hf_api_token(api_token)

    for module_name in (
        "script_maker",
        "scene_maker",
        "photo_generator",
        "voice_recorder",
    ):
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])

    if "main" in sys.modules:
        main_module = importlib.reload(sys.modules["main"])
    else:
        main_module = importlib.import_module("main")

    return main_module.generate_short_video


def save_client_json(uploaded_file):
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / "client_secret.json"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


# =====================================================
# Page Config
# =====================================================

st.set_page_config(
    page_title="AI Video Maker",
    layout="wide"
)

st.title("🎬 AI Video Maker")


# =====================================================
# Session State
# =====================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "show_upload" not in st.session_state:
    st.session_state.show_upload = False


# =====================================================
# Sidebar
# =====================================================

with st.sidebar:

    st.header("🎬 Video Settings")

    hf_api_token = st.text_input(
        "Hugging Face API Token",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxxx"
    )

    with st.expander("📖 How to get a Hugging Face API Token"):
        st.markdown("""
### Step 1
Create a free Hugging Face account.

https://huggingface.co

### Step 2
Open Access Tokens.

https://huggingface.co/settings/tokens

### Step 3
Click **Create New Token**

### Step 4
Choose:

- Read permissions
- Inference permissions

### Step 5
Copy the token that looks like:

hf_xxxxxxxxxxxxxxxxxxxxxxxxx

### Step 6
Paste the token into the field above.

⚠️ Your token is only used to generate videos.
        """)

    topic = st.text_input(
        "Video Topic",
        placeholder="Interesting Space Facts"
    )

    output_folder = st.text_input(
        "Output Folder (Optional)"
    )

    generate_clicked = st.button(
        "Generate Video",
        type="primary",
        use_container_width=True
    )

# =====================================================
# Generate Video
# =====================================================

if generate_clicked:

    topic = topic.strip()
    output_folder = output_folder.strip() or None
    hf_api_token = resolve_hf_api_token(hf_api_token)

    if not topic:
        st.error("Please enter a topic.")

    elif not hf_api_token:
        st.error("Please enter your Hugging Face API token.")

    else:

        try:

            with st.status(
                "Generating video...",
                expanded=True
            ) as status:

                generate_short_video = load_generator(
                    hf_api_token
                )

                def report(message):
                    st.write(message)

                result = generate_short_video(
                    topic,
                    output_folder,
                    status_callback=report
                )

                st.session_state.result = result
                st.session_state.show_upload = False

                status.update(
                    label="Video generated successfully!",
                    state="complete"
                )

        except Exception as e:
            st.exception(e)


# =====================================================
# Display Generated Video
# =====================================================

result = st.session_state.result

if result:

    st.divider()

    st.subheader(result["video_name"])

    video_file = Path(result["video_file"])

    if video_file.exists():

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.video(str(video_file))
        

        # Download button
        with open(video_file, "rb") as f:

            st.download_button(
                label="⬇ Download Video",
                data=f.read(),
                file_name=video_file.name,
                mime="video/mp4",
                use_container_width=True
            )

        st.divider()

        # Upload Button
        if not st.session_state.show_upload:
            from streamlit_oauth import OAuth2Component

            oauth2 = OAuth2Component(
                client_id=st.secrets["GOOGLE_CLIENT_ID"],
                client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
                authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
            )

            result = oauth2.authorize_button(
                name="Connect YouTube",
                redirect_uri="https://your-app.streamlit.app/component/streamlit_oauth.authorize_button",
                scope="https://www.googleapis.com/auth/youtube.upload",
                
)
            if result:
                st.session_state["google_token"] = result["token"]
                
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials(
                token=st.session_state["google_token"]["access_token"]
            )

            youtube = build(
                "youtube",
                "v3",
                credentials=creds
            )    

            if st.button("Upload To YouTube"):

                upload_video(
                    youtube=youtube,
                    topic=result["video_name"],
                    script=result["script"],
                    video_file=video_file
    )
            
                st.session_state.show_upload = True
                st.rerun()

        # =================================================
        # YouTube Upload Section
        # =================================================

        if st.session_state.show_upload:

            st.subheader("📺 Upload To YouTube")

            st.success("""
        ✅ Video generated successfully.

        To upload it to YouTube, follow the instructions below.
        """)

            st.link_button(
                "🎥 Watch Setup Tutorial",
                "https://youtu.be/aBwyDZS8HUc?si=l7k55dXC4dXVh-JX"
            )

            with st.expander(
                "📖 How to get client_secret.json and enable YouTube uploads"
            ):

                st.markdown("""
        ### Step 1 — Open Google Cloud Console

        https://console.cloud.google.com

        ### Step 2 — Create a Project

        Click:

        New Project

        Example:

        AI Video Maker

        ### Step 3 — Enable YouTube Data API v3

        Go to:

        APIs & Services
        → Library

        Search:

        YouTube Data API v3

        Click:

        ENABLE

        ### Step 4 — Configure OAuth Consent Screen

        Go to:

        APIs & Services
        → OAuth Consent Screen

        Choose:

        External

        Fill:

        - App Name
        - Your Email

        Save

        ### Step 5 — Create OAuth Credentials

        Go to:

        APIs & Services
        → Credentials

        Create Credentials
        → OAuth Client ID

        Application Type:

        Desktop Application

        Click Create

        ### Step 6 — Download JSON File

        Download:

        client_secret.json

        ### Step 7 — Upload It Below

        After uploading, Google will open a login page.

        Sign in to the YouTube account where you want the video uploaded.

        ### Permissions Requested

        This application requests:

        ✅ Upload videos

        ✅ Manage uploaded videos

        It DOES NOT request:

        ❌ Gmail access

        ❌ Google Drive access

        ❌ Google Photos access
        """)

            client_json = st.file_uploader(
                "Upload client_secret.json",
                type=["json"]
            )

            if client_json:

                st.success(
                    "client_secret.json uploaded successfully."
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "🚀 Upload Video",
                        type="primary",
                        use_container_width=True
                    ):

                        try:

                            client_path = save_client_json(
                                client_json
                            )

                            with st.spinner(
                                "Opening Google Login..."
                            ):

                                youtube = authenticate_youtube(
                                    str(client_path)
                                )

                            with st.spinner(
                                "Uploading video..."
                            ):

                                upload_video(
                                    youtube=youtube,
                                    topic=result["video_name"],
                                    script=result.get(
                                        "script",
                                        ""
                                    ),
                                    video_file=video_file
                                )

                            st.success(
                                "🎉 Video uploaded successfully!"
                            )

                        except Exception as e:
                            st.exception(e)

                with col2:

                    if st.button(
                        "Cancel Upload",
                        use_container_width=True
                    ):
                        st.session_state.show_upload = False
                        st.rerun()

    else:
        st.error(
            f"Video file not found: {video_file}"
        )