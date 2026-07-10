import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Skin-Journal", 
    page_icon="✨", 
    layout="centered"
)

# 2. Your Google Sheet ID
SHEET_ID = "1eERvp1bG9xnhg-Tx2uVqalrCVsTHW2DeZWHwcSrOyoE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# 3. Try to read cloud database
try:
    df = pd.read_csv(CSV_URL)
except Exception as e:
    df = pd.DataFrame(columns=["date", "skincare"])

st.title("✨ Skin-Journal")
st.subheader("Your Evidence-Based Skincare Tracker")
st.markdown("---")

# 4. Create App Tabs
tab1, tab2 = st.tabs(["✍️ Daily Log", "📊 History Insights"])

# --- TAB 1: Daily Log ---
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
            new_row = pd.DataFrame([{"date": today_str, "skincare": skincare_used}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            st.success("🎉 Successfully synced with your cloud Google Sheet!")
            st.balloons()
            st.dataframe(new_row)
        else:
            st.error("⚠️ Please fill in your skincare products before saving.")

# --- TAB 2: History Table ---
with tab2:
    st.header("📈 Skincare Journey Timeline")
    
    if df.empty:
        st.info("No logs found yet. Start your first entry in the Daily Log!")
    else:
        # Render clean interactive data table
        st.dataframe(
            df.sort_values(by="date", ascending=False), 
            use_container_width=True,
            hide_index=True
        )
        
        # Display stats metric
        total_days = len(df['date'].unique())
        st.metric(label="Total Days Logged", value=f"{total_days} Days")
