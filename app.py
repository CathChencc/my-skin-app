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

# 3. Try to read cloud database
try:
    df = pd.read_csv(CSV_URL)
    # Ensure columns exist if sheet is fresh
    if "username" not in df.columns:
        df["username"] = "guest"
except Exception as e:
    df = pd.DataFrame(columns=["date", "skincare", "username"])

st.title("✨ Skin-Journal")
st.subheader("Multi-Device Cloud Sync Version")
st.markdown("---")

# 👤 核心功能：左側側邊欄——使用者登入系統
with st.sidebar:
    st.header("👤 User Account")
    user_input = st.text_input("Enter your username to login/sync:", "guest").strip()
    
    if user_input == "" or user_input == "guest":
        st.warning("Currently viewing as: Guest")
    else:
        st.success(f"Logged in as: {user_input}")
    
    st.markdown("""
    💡 **How Multi-Device Sync Works:**
    Type the exact same username on your computer, phone, or tablet to access your identical skincare history instantly!
    """)

# 4. Filter data based on logged-in user
user_df = df[df["username"] == user_input]

# 5. Create App Tabs
tab1, tab2, tab3 = st.tabs(["✍️ Daily Log", "📊 History Insights", "🎬 Monthly Time-lapse"])

# --- TAB 1: Daily Log (寫入時自動綁定當前帳號) ---
with tab1:
    st.header(f"Record for [{user_input}]")
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"Today is: {today_str}")
    
    uploaded_file = st.file_uploader("📸 Snap your skin condition today", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Today's Snapshot", width=300)
        
    skincare_used = st.text_area(
        "🧴 What skincare routine did you use today?", 
        placeholder="e.g., Retinol, Hyaluronic Acid, Vitamin C..."
    )
    
    if st.button("🚀 Save to Cloud Database"):
        if skincare_used.strip() != "":
            # 關鍵：將 date, skincare, username 三合一打包
            new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used, "username": user_input}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save Image to local folder prefixed with username for isolation
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                img_path = os.path.join(IMAGE_DIR, f"{user_input}_{today_str}.jpg")
                img.save(img_path)
            
            st.success(f"🎉 Saved successfully! Automatically linked to account: {user_input}")
            st.balloons()
            st.dataframe(new_row)
        else:
            st.error("⚠️ Please fill in your skincare products before saving.")

# --- TAB 2: History Table (只顯示該登入帳號的數據) ---
with tab2:
    st.header(f"📊 {user_input}'s Skincare Timeline")
    
    if user_df.empty:
        st.info(f"No logs found for user '{user_input}'. Start logging today!")
    else:
        st.dataframe(
            user_df.sort_values(by="date", ascending=False), 
            use_container_width=True,
            hide_index=True
        )
        total_days = len(user_df['date'].unique())
        st.metric(label="Total Days Logged", value=f"{total_days} Days")

# --- TAB 3: Monthly Time-lapse (只讀取該帳號的照片生成縮時) ---
with tab3:
    st.header("🎬 Generate Monthly Evolution Video")
    st.write(f"Compiling cached daily photos for account: **{user_input}**")
    
    if st.button("🚀 Generate Time-lapse Video"):
        # Fetch photos that match the current user's prefix
        photo_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.startswith(f"{user_input}_") and f.endswith(".jpg")])
        
        if len(photo_files) < 2:
            st.warning(f"提示：帳號【{user_input}】儲存的照片太少（小於 2 張），多記錄幾天再來生成影片吧！")
        else:
            output_video_path = f"{user_input}_skin_evolution.mp4"
            
            first_img_path = os.path.join(IMAGE_DIR, photo_files[0])
            first_img = cv2.imread(first_img_path)
            height, width, layers = first_img.shape
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_video_path, fourcc, 2, (width, height))
            
            for photo in photo_files:
                img_path = os.path.join(IMAGE_DIR, photo)
                img = cv2.imread(img_path)
                img_resized = cv2.resize(img, (width, height))
                video.write(img_resized)
                
            video.release()
            st.success("✨ Your monthly skin evolution video is ready!")
            
            with open(output_video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
