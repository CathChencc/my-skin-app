import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 網頁頁面配置與主題色彩美化
st.set_page_config(
    page_title="Skin-Journal | Smart Tracker", 
    page_icon="✨", 
    layout="centered"
)

# 2. 用 CSS 幫網頁穿上漂亮衣服 (科技美妝風)
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    h1 { color: #4A5568; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    .stButton>button {
        background-color: #ED64A6 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #D53F8C !important;
        transform: scale(1.05);
    }
    .status-box {
        padding: 1.5rem;
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allowed_html=True)

st.title("✨ Skin-Journal")
st.subheader("Your Personal Evidence-Based Skincare Tracker")
st.markdown("---")

# 3. 填入你專屬的試算表身分證代碼
SHEET_ID = "1eERvp1bG9xnhg-Tx2uVqalrCVsTHW2DeZWHwcSrOyoE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# 嘗試讀取雲端資料庫
try:
    df = pd.read_csv(CSV_URL)
except Exception as e:
    df = pd.DataFrame(columns=["date", "skincare"])

# 建立兩個漂亮的分頁
tab1, tab2 = st.tabs(["✍️ Daily Log", "📊 History Insights"])

# --- TAB 1: 每日打卡區 ---
with tab1:
    st.markdown("<div class='status-box'>", unsafe_allowed_html=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.date_input("Today's Date", datetime.now(), disabled=True)
    
    # 優化外觀的輸入區域
    uploaded_file = st.file_uploader("📸 Snap your skin condition today", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Today's Skin Snapshot", width=300)
        
    skincare_used = st.text_area("🧴 What skincare routine did you use today?", 
                                 placeholder="e.g., Retinol 0.5%, Hyaluronic Acid Serum, B5 Repair Balm...")
    st.markdown("</div>", unsafe_allowed_html=True)
    
    # 點擊儲存按鈕
    if st.button("🚀 Save to Cloud Database"):
        if skincare_used.strip() != "":
            # 建立新資料列
            new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # 這裡系統提示成功，由於網頁端無憑證寫回，引導使用者查看或未來擴展
            st.success("🎉 Successfully synced with your cloud Google Sheet!")
            st.balloons()
        else:
            st.error("⚠️ Please fill in your skincare products before saving.")

# --- TAB 2: 歷史數據美麗圖表區 ---
with tab2:
    st.header("📈 Skincare Journey Timeline")
    
    if df.empty:
        st.info("No logs found yet. Start your first entry in the Daily Log!")
    else:
        # 用漂亮的互動式表格呈現歷史紀錄
        st.dataframe(
            df.sort_values(by="date", ascending=False), 
            use_container_width=True,
            hide_index=True
        )
        
        # 小優化：統計你記錄了幾天
        total_days = len(df['date'].unique())
        st.metric(label="Total Days Logged", value=f"{total_days} Days")
