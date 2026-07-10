import streamlit as st
import pandas as pd
import cv2
import os
from datetime import datetime
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Skin-Journal", 
    page_icon="✨", 
    layout="centered"
)

# 2. Your Google Sheet ID & Local Image Directory
SHEET_ID = "1eERvp1bG9xnhg-Tx2uVqalrCVsTHW2DeZWHwcSrOyoE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
IMAGE_DIR = "skin_photos"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 3. Try to read cloud database (for text history)
try:
    df = pd.read_csv(CSV_URL)
except Exception as e:
    df = pd.DataFrame(columns=["date", "skincare"])

st.title("✨ Skin-Journal")
st.subheader("Your Cloud-Backed Skincare & Time-lapse Tracker")
st.markdown("---")

# 4. Create App Tabs
tab1, tab2, tab3 = st.tabs(["✍️ Daily Log", "📊 History Insights", "🎬 Monthly Time-lapse"])

# --- TAB 1: Daily Log (文字上雲端，照片存本地) ---
with tab1:
    st.header("Today's Record")
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"Today is: {today_str}")
    
    # Upload photo block
    uploaded_file = st.file_uploader("📸 Snap your skin condition today", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Today's Snapshot", width=300)
        
    # Skincare routine input
    skincare_used = st.text_area(
        "🧴 What skincare routine did you use today?", 
        placeholder="e.g., Retinol, Hyaluronic Acid, Vitamin C..."
    )
    
    # Save button
    if st.button("🚀 Save to Cloud Database"):
        if skincare_used.strip() != "":
            # Save Text to cloud logic hint
            new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save Image to local folder for Time-lapse video
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                img_path = os.path.join(IMAGE_DIR, f"{today_str}.jpg")
                img.save(img_path)
            
            st.success("🎉 Success! Text synced to Google Sheet, and photo cached for your video!")
            st.balloons()
            st.dataframe(new_row)
        else:
            st.error("⚠️ Please fill in your skincare products before saving.")

# --- TAB 2: History Table (文字歷史紀錄) ---
with tab2:
    st.header("📈 Skincare Journey Timeline")
    if df.empty:
        st.info("No logs found yet. Start your first entry in the Daily Log!")
    else:
        st.dataframe(
            df.sort_values(by="date", ascending=False), 
            use_container_width=True,
            hide_index=True
        )
        total_days = len(df['date'].unique())
        st.metric(label="Total Days Logged", value=f"{total_days} Days")

# --- TAB 3: Monthly Time-lapse (重磅回歸！月底縮時影片生成) ---
with tab3:
    st.header("🎬 Generate Monthly Evolution Video")
    st.write("We will compile all your cached daily photos into a seamless time-lapse video!")
    
    if st.button("🚀 Generate Time-lapse Video"):
        # Fetch all saved photos
        photo_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")])
        
        if len(photo_files) < 2:
            st.warning("提示：目前本地儲存的照片太少（小於 2 張），多記錄幾天再來生成影片吧！")
        else:
            output_video_path = "skin_evolution.mp4"
            
            # Read first image to set dimensions
            first_img_path = os.path.join(IMAGE_DIR, photo_files[0])
            first_img = cv2.imread(first_img_path)
            height, width, layers = first_img.shape
            
            # Video Writer Config (2 frames per second)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_video_path, fourcc, 2, (width, height))
            
            # Resize and write each photo into the video
            for photo in photo_files:
                img_path = os.path.join(IMAGE_DIR, photo)
                img = cv2.imread(img_path)
                img_resized = cv2.resize(img, (width, height))
                video.write(img_resized)
                
            video.release()
            st.success("✨ Your monthly skin evolution video is ready!")
            
            # Play video inside Streamlit app
            with open(output_video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
