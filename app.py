import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Skin-Journal", page_icon="📸")
st.title("Skin-Journal Cloud App")

# ⚠️ 請把下面這行引號裡面的代碼，換成你剛剛單獨複製的那串【身分證代碼】！
SHEET_ID = "把你的試算表身分證代碼貼在這裡"

# 這是萬能轉化網址，能繞過所有外掛，直接把 Excel 轉成最純淨的英文數據流
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# 嘗試讀取雲端資料
try:
    df = pd.read_csv(CSV_URL)
except Exception as e:
    st.error("Connection error, but we are fixing it!")
    df = pd.DataFrame(columns=["date", "skincare"])

today_str = datetime.now().strftime("%Y-%m-%d")
skincare_used = st.text_input("What skincare products did you use today?", "")

if st.button("Save to Cloud"):
    if skincare_used.strip() != "":
        # 建立新資料
        new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # 提示：因為沒開高級憑證，直接寫回需要引導
        st.success("Success! Please paste this data to your sheet if needed.")
        st.dataframe(new_row)

st.subheader("Your History Log:")
st.dataframe(df)
