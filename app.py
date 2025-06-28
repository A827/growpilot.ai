
import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="GrowPilot.ai", layout="wide")

# --- Modern UI Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Manrope', sans-serif;
    background-color: #f7f9fc;
    color: #1f2937;
}
.sidebar .sidebar-content {
    background-color: #e5f4ec;
}
h1, h2, h3 {
    color: #10b981;
}
.stButton > button {
    background-color: #10b981;
    color: white;
    padding: 0.6em 1.2em;
    border: none;
    border-radius: 10px;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #059669;
}
.card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Session State Storage ---
if "data" not in st.session_state:
    st.session_state.data = {
        "plants": [],
        "watering": [],
        "nutrients": [],
        "harvests": []
    }

def save_entry(section, entry):
    st.session_state.data[section].append(entry)

def to_df(section):
    return pd.DataFrame(st.session_state.data[section])

# --- Sidebar Navigation ---
st.sidebar.title("🌿 GrowPilot.ai")
page = st.sidebar.radio("Navigate", ["Dashboard", "Add Plant", "Log Watering", "Log Nutrients", "Log Harvest", "Export Data"])

# --- Dashboard ---
if page == "Dashboard":
    st.title("📊 GrowPilot.ai – Smart Growing Dashboard")
    st.markdown("Track your progress, harvests, and predictions below.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Harvest Summary")
    harvest_df = to_df("harvests")
    if not harvest_df.empty:
        harvest_df["Date"] = pd.to_datetime(harvest_df["Date"])
        daily = harvest_df.groupby("Date")["Grams"].sum().reset_index()
        st.line_chart(daily.set_index("Date"))
    else:
        st.info("No harvest data yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    if not harvest_df.empty:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 AI Harvest Prediction")
        harvest_df["Days"] = (harvest_df["Date"] - harvest_df["Date"].min()).dt.days
        model = LinearRegression()
        X = harvest_df[["Days"]]
        y = harvest_df["Grams"]
        model.fit(X, y)
        future = pd.DataFrame({"Days": range(X["Days"].max()+1, X["Days"].max()+15)})
        preds = model.predict(future)
        fig, ax = plt.subplots()
        ax.plot(harvest_df["Date"], y, label="Actual")
        future_dates = [harvest_df["Date"].min() + pd.Timedelta(days=int(i)) for i in future["Days"]]
        ax.plot(future_dates, preds, label="Forecast", linestyle="--")
        ax.set_title("Forecasted Yield")
        ax.legend()
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

# --- Add Plant ---
elif page == "Add Plant":
    st.title("🌱 Add a New Planting")
    name = st.text_input("Plant Name")
    date = st.date_input("Planting Date", datetime.today())
    if st.button("Add Plant"):
        save_entry("plants", {"Name": name, "Date Planted": date})
        st.success(f"Added {name}")

# --- Log Watering ---
elif page == "Log Watering":
    st.title("💧 Watering Log")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Date", datetime.today())
    amount = st.number_input("Liters", 0.0)
    if st.button("Save Watering"):
        save_entry("watering", {"Plant": plant, "Date": date, "Liters": amount})
        st.success("Watering saved.")

# --- Log Nutrients with Webcam Support ---
elif page == "Log Nutrients":
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
    import av
    import cv2
    import numpy as np

    st.title("🧪 Nutrient Entry")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Date", datetime.today())

    method = st.radio("How would you like to input the nutrient label?", ["Upload Image", "Use Webcam"])

    captured_image = None

    if method == "Upload Image":
        image = st.file_uploader("Upload Image of Nutrient Product", type=["jpg", "jpeg", "png"])
        if image:
            st.image(image, caption="Uploaded Image", use_column_width=True)
            st.warning("Please enter the product name manually below.")
    else:
        st.info("📷 Allow webcam access below to capture label")
        class CameraCapture(VideoTransformerBase):
            def __init__(self):
                self.frame = None
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                self.frame = img
                return img

        ctx = webrtc_streamer(key="label-cam", video_transformer_factory=CameraCapture)

        if ctx.video_transformer and ctx.video_transformer.frame is not None:
            captured_image = ctx.video_transformer.frame
            st.image(captured_image, caption="Captured Frame", use_column_width=True)
            st.warning("Please enter the product name manually below.")

    product = st.text_input("Product Name")
    notes = st.text_area("Notes (Optional)")

    if st.button("Save Nutrient Log"):
        save_entry("nutrients", {"Plant": plant, "Date": date, "Product": product, "Notes": notes})
        st.success("✅ Nutrient log saved.")
        
        
# --- Log Harvest ---
elif page == "Log Harvest":
    st.title("🍅 Harvest Log")
    plant = st.selectbox("Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Date", datetime.today())
    grams = st.number_input("Harvest Weight (grams)", 0.0)
    if st.button("Log Harvest"):
        save_entry("harvests", {"Plant": plant, "Date": date, "Grams": grams})
        st.success("Harvest added.")

# --- Export ---
elif page == "Export Data":
    st.title("📤 Export Data Logs")
    for section in st.session_state.data:
        df = to_df(section)
        st.download_button(
            f"Download {section.title()} CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{section}.csv",
            mime="text/csv"
        )
