import streamlit as st
import pandas as pd
import cv2
import os
import requests
from datetime import datetime
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Skin-Journal", page_icon="✨", layout="centered")

# 2. 雲端資料庫設定區域 (填入你自己的資訊)
SHEET_ID = "1eERvp1bG9xnhg-Tx2uVqalrCVsTHW2DeZWHwcSrOyoE"
# ⚠️ 注意：因為表單連過去後會變成第二個分頁，格式改成讀取「表單回覆 1」
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=985156230"

# ⚠️ 請把下面這行換成你剛剛建立的 Google 表單網址 (結尾改成 /formResponse)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf2jXtbtY0P3UMdBOVyzxdp8xZg9JkGyzKAhO5ZIi0iI97NvA/formResponse"

IMAGE_DIR = "skin_photos"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 3. 讀取雲端試算表歷史紀錄
try:
    df = pd.read_csv(CSV_URL)
    # 防呆：如果雲端只有時間戳記，手動對齊欄位名稱
    df.columns = [c.strip() for c in df.columns]
    # Google表單預設第一欄是時間戳記，所以我們對應後面的欄位
    if "username" not in df.columns:
        df["username"] = "guest"
except Exception as e:
    df = pd.DataFrame(columns=["date", "skincare", "username"])

st.title("✨ Skin-Journal")
st.subheader("Real-Time Multi-Device Cloud Sync")
st.markdown("---")

# 左側側邊欄：使用者帳號同步系統
with st.sidebar:
    st.header("👤 User Account")
    user_input = st.text_input("Enter your username to login/sync:", "guest").strip()
    if user_input == "" or user_input == "guest":
        st.warning("Currently viewing as: Guest")
    else:
        st.success(f"Logged in as: {user_input}")

# 過濾出當前登入帳號的專屬歷史紀錄
# 由於表單名稱可能大小寫有差，這邊做個防呆
if not df.empty and "username" in df.columns:
    user_df = df[df["username"].astype(str) == str(user_input)]
else:
    user_df = pd.DataFrame(columns=["date", "skincare", "username"])

tab1, tab2, tab3 = st.tabs(["✍️ Daily Log", "📊 History Insights", "🎬 Monthly Time-lapse"])

# --- TAB 1: Daily Log (這次要實打實寫回雲端了！) ---
with tab1:
    st.header(f"Record for [{user_input}]")
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"Today is: {today_str}")
    
    uploaded_file = st.file_uploader("📸 Snap your skin condition today", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Today's Snapshot", width=300)
        
    skincare_used = st.text_area("🧴 What skincare routine did you use today?", placeholder="e.g., Retinol...")
    
    if st.button("🚀 Save to Cloud Database"):
        if skincare_used.strip() != "":
            # 💡 核心魔法：利用 requests 偷偷把資料送到 Google 表單，直接寫入 Google 試算表！
            # ⚠️ 請把下方的 entry.XXXXX 換成你剛剛在步驟二查到的神祕數字標籤！
            form_data = {
                "entry.547169018": today_str,       # 換成你 date 的 entry 代碼
                "entry.1706698188": skincare_used,   # 換成你 skincare 的 entry 代碼
                "entry.1444146746": user_input       # 換成你 username 的 entry 代碼
            }
            
            try:
                # 實打實發送出去！
                response = requests.post(FORM_URL, data=form_data)
                
                # 本地照片快取保留（供月底縮時影片使用）
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    img.save(os.path.join(IMAGE_DIR, f"{user_input}_{today_str}.jpg"))
                
                st.success("🎉 Data permanent saved to cloud! Please refresh in 5 seconds to see updates.")
                st.balloons()
            except Exception as write_error:
                st.error(f"Cloud write failed: {write_error}")
        else:
            st.error("⚠️ Please fill in your skincare products before saving.")

# --- TAB 2: History Table ---
with tab2:
    st.header(f"📊 {user_input}'s Skincare Timeline")
    if user_df.empty:
        st.info(f"No permanent logs found for '{user_input}'. Try logging and refreshing!")
    else:
        # 顯示除了時間戳記以外的乾淨欄位
        show_cols = [col for col in user_df.columns if "時間戳記" not in col and "Timestamp" not in col]
        st.dataframe(user_df[show_cols].sort_values(by=show_cols[0], ascending=False), use_container_width=True, hide_index=True)
        total_days = len(user_df[show_cols[0]].unique())
        st.metric(label="Total Days Logged", value=f"{total_days} Days")

# --- TAB 3: Monthly Time-lapse ---
with tab3:
    st.header("🎬 Generate Monthly Evolution Video")
    if st.button("🚀 Generate Time-lapse Video"):
        photo_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.startswith(f"{user_input}_") and f.endswith(".jpg")])
        if len(photo_files) < 2:
            st.warning("提示：照片不足 2 張，多記錄幾天再來吧！")
        else:
            output_video_path = f"{user_input}_skin_evolution.mp4"
            first_img = cv2.imread(os.path.join(IMAGE_DIR, photo_files[0]))
            h, w, _ = first_img.shape
            video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 2, (w, h))
            for photo in photo_files:
                img = cv2.resize(cv2.imread(os.path.join(IMAGE_DIR, photo)), (w, h))
                video.write(img)
            video.release()
            st.success("✨ Video Ready!")
            with open(output_video_path, 'rb') as vf:
                st.video(vf.read())
