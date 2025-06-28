
import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from PIL import Image
from pyzbar.pyzbar import decode
import io

st.set_page_config(page_title="GrowPilot.ai", layout="wide")

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

# --- Sidebar ---
st.sidebar.title("🌿 GrowPilot.ai")
page = st.sidebar.radio("Navigate", ["Dashboard", "Add Plant", "Log Watering", "Log Nutrients", "Log Harvest", "Export Data"])

# --- Nutrient Log with Barcode Scanner ---
if page == "Log Nutrients":
    st.title("🧪 Nutrient Entry")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Date", datetime.today())

    st.subheader("📷 Scan Barcode")
    barcode_result = None
    uploaded_image = st.file_uploader("Upload Barcode Image", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Barcode", use_column_width=True)
        decoded = decode(image)
        if decoded:
            barcode_result = decoded[0].data.decode("utf-8")
            st.success(f"✅ Barcode Detected: {barcode_result}")
        else:
            st.warning("❌ No barcode detected. Try another image.")

    product_name = st.text_input("Product Used", value=barcode_result if barcode_result else "")
    notes = st.text_area("Notes")

    if st.button("Save Nutrient Log"):
        save_entry("nutrients", {"Plant": plant, "Date": date, "Product": product_name, "Notes": notes})
        st.success("Nutrient recorded.")

# (Other sections omitted for brevity — identical to v2)
