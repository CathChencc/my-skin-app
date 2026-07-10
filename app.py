import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Skin-Journal", page_icon="📸")
st.title("Skin-Journal Cloud App")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data
df = conn.read(ttl=0) 

today_str = datetime.now().strftime("%Y-%m-%d")
skincare_used = st.text_input("What skincare products did you use today?", "")

if st.button("Save to Cloud"):
    if skincare_used.strip() != "":
        # Create a new data row
        new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Update Google Sheets
        conn.update(data=df)
        st.success("Success! Data saved to your Google Sheet.")

st.subheader("Your History Log:")
st.dataframe(df)
