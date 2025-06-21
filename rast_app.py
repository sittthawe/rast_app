import streamlit as st
import os
import uuid
import time
import io
from PIL import Image, UnidentifiedImageError

# === Constants ===
PHOTO_DIR = "media/photos"
VIDEO_DIR = "media/videos"
UPLOAD_PASSWORD = "rast2611"

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# === Set Page Config ===
st.set_page_config(page_title="Photo Video Album", layout="wide")

# === Custom CSS ===
st.markdown("""
    <style>
        .stApp {
            animation: fadeIn 1.2s ease-in;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        .animated-text {
            animation: slideIn 1s ease-in-out;
        }
        @keyframes slideIn {
            from {transform: translateY(-20px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
        .css-1aumxhk, .stButton>button {
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00f5a0;
            color: black;
            transform: scale(1.05);
        }
        .gallery-media {
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 0 15px rgba(0,255,255,0.2);
        }
    </style>
""", unsafe_allow_html=True)

# === Utility Functions ===
def save_file(file, folder):
    file_ext = file.name.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_ext}"
    filepath = os.path.join(folder, unique_name)
    with open(filepath, "wb") as f:
        f.write(file.read())
    return unique_name

def list_files(folder):
    return [f for f in os.listdir(folder) if not f.startswith(".")]

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def verify_password():
    password = st.text_input("Enter Password to Proceed", type="password", key="password_input")
    if password:
        st.session_state["authenticated"] = (password == UPLOAD_PASSWORD)
    return st.session_state.get("authenticated", False)

# === Tabs ===
tab1, tab2 = st.tabs(["Gallery", "Uploads"])

# === GALLERY TAB ===
with tab1:
    st.markdown("<h2 class='animated-text'>📸 Gallery</h2>", unsafe_allow_html=True)
    videos = list_files(VIDEO_DIR)
    photos = list_files(PHOTO_DIR)

    # Show Videos first
    st.subheader("Videos")
    cols = st.columns(2)
    for i, video in enumerate(videos):
        vid_path = os.path.join(VIDEO_DIR, video)
        with cols[i % 2]:
            try:
                with open(vid_path, "rb") as file:
                    video_bytes = file.read()
                    st.video(video_bytes, format="video/mp4", start_time=0)
            except Exception:
                st.warning(f"⚠️ Could not load video: {video}")

    # Then show Photos
    st.subheader("Photos")
    cols = st.columns(4)
    for i, photo in enumerate(photos):
        img_path = os.path.join(PHOTO_DIR, photo)
        try:
            with open(img_path, "rb") as file:
                img_bytes = file.read()
                Image.open(io.BytesIO(img_bytes))  # Validate image
                with cols[i % 4]:
                    st.image(img_bytes, use_container_width=True, caption=photo)
        except (UnidentifiedImageError, IOError):
            st.warning(f"⚠️ Skipped invalid image file: {photo}")

# === UPLOAD TAB ===
with tab2:
    st.markdown("<h2 class='animated-text'>📤 Upload Media</h2>", unsafe_allow_html=True)

    if verify_password():
        st.subheader("Upload Photos")
        photo_files = st.file_uploader("Choose photo(s)", type=["jpg", "jpeg", "png"], key="photos", accept_multiple_files=True)
        if photo_files and st.button("Upload Photo(s)"):
            for file in photo_files:
                save_file(file, PHOTO_DIR)
            st.success("Photos uploaded successfully.")

        st.subheader("Upload Videos")
        video_files = st.file_uploader("Choose video(s)", type=["mp4", "mov"], key="videos", accept_multiple_files=True)
        if video_files and st.button("Upload Video(s)"):
            for file in video_files:
                save_file(file, VIDEO_DIR)
            st.success("Videos uploaded successfully.")

        st.subheader("Delete Files")
        file_type = st.selectbox("Select file type", ["Photo", "Video"])
        folder = PHOTO_DIR if file_type == "Photo" else VIDEO_DIR
        file_list = list_files(folder)
        if file_list:
            files_to_delete = st.multiselect("Choose file(s) to delete", file_list)
            if files_to_delete and st.button("Delete Selected Files"):
                for f in files_to_delete:
                    delete_file(os.path.join(folder, f))
                st.success("Selected file(s) deleted successfully.")
        else:
            st.info(f"No {file_type.lower()}s available to delete.")
    else:
        st.info("Please enter the password to unlock upload and delete options.")
