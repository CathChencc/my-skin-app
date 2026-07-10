%%writefile app.py
import streamlit as st
import pandas as pd
import cv2
import os
from datetime import datetime
from PIL import Image

# 建立儲存照片與文字的祕密基地
IMAGE_DIR = "skin_photos"
CSV_FILE = "skin_log.csv"
os.makedirs(IMAGE_DIR, exist_ok=True)

st.set_page_config(page_title="Skin-Journal", page_icon="📸")
st.title("📸 Skin-Journal 膚況縮時紀錄 App")
st.write("Google Colab 雲端測試版：每日打卡 ✕ 月底自動生成回顧影片！")

tab1, tab2 = st.tabs(["📅 每日膚況打卡", "🎬 月底影片生成"])

with tab1:
    st.header("今日膚況與保養紀錄")
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"今天是：{today_str}")
    
    uploaded_file = st.file_uploader("👉 第一步：拍一張今天的臉部照片", type=["jpg", "jpeg", "png"])
    skincare_used = st.text_input("👉 第二步：今天擦了什麼保養品？", "")
    
    if st.button("💾 儲存今日紀錄"):
        if uploaded_file is not None and skincare_used.strip() != "":
            img = Image.open(uploaded_file)
            img_path = os.path.join(IMAGE_DIR, f"{today_str}.jpg")
            img.save(img_path)
            
            new_data = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
                df = df[df["date"] != today_str]
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                df = new_data
            df.to_csv(CSV_FILE, index=False)
            st.success(f"🎉 儲存成功！照片與保養品都幫你記下來囉。")
        else:
            st.error("❌ 儲存失敗：請檢查是不是忘記上傳照片，或是保養品格子留白了？")

with tab2:
    st.header("🎬 產生本月膚況縮時影片")
    if st.button("🚀 一鍵生成縮時影片"):
        photo_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")])
        if len(photo_files) < 2:
            st.warning(" 提示：目前儲存的照片太少（小於 2 張），多記錄幾天再來生成影片吧！")
        else:
            output_video_path = "skin_evolution.mp4"
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
            st.success("✨ 縮時影片製作完成！")
            
            with open(output_video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
