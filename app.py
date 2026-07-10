import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Skin-Journal", page_icon="📸")
st.title("📸 Skin-Journal 雲端商業版")

# 建立雲端資料庫連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取現有的雲端紀錄
df = conn.read(ttl=0) 

today_str = datetime.now().strftime("%Y-%m-%d")
skincare_used = st.text_input("今天擦了什麼保養品？（例如：保濕乳液、A醇精華）", "")

if st.button("💾 儲存到雲端"):
    if skincare_used.strip() != "":
        # 增加新的一行資料
        new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # 一鍵寫回 Google Sheet！
        conn.update(data=df)
        st.success("資料已永久寫入你的 Google 雲端試算表！重新整理也不會丟失了！")

st.subheader("📖 你的歷史保養打卡紀錄：")
st.dataframe(df)
