
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="GrowPilot.ai", layout="wide")

# --- Initialize Data Storage ---
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
page = st.sidebar.radio("Navigate", ["Dashboard", "Add Plant", "Watering Log", "Nutrient Log", "Harvest Entry", "Export Data"])

# --- Add Plant ---
if page == "Add Plant":
    st.header("🌱 Add New Planting")
    name = st.text_input("Plant Variety")
    plant_date = st.date_input("Planting Date", datetime.today())
    if st.button("Add Plant"):
        save_entry("plants", {"Name": name, "Date Planted": plant_date})
        st.success(f"Added {name} planted on {plant_date}")

# --- Watering Log ---
elif page == "Watering Log":
    st.header("💧 Watering Entry")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Watering Date", datetime.today())
    amount = st.number_input("Water Amount (L)", min_value=0.0, step=0.1)
    if st.button("Log Watering"):
        save_entry("watering", {"Plant": plant, "Date": date, "Amount (L)": amount})
        st.success("Watering logged.")

# --- Nutrient Log ---
elif page == "Nutrient Log":
    st.header("🧪 Nutrient Entry")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Application Date", datetime.today())
    nutrient = st.text_input("Nutrient/Fertilizer Name")
    notes = st.text_area("Notes")
    if st.button("Log Nutrient"):
        save_entry("nutrients", {"Plant": plant, "Date": date, "Nutrient": nutrient, "Notes": notes})
        st.success("Nutrient added.")

# --- Harvest Entry ---
elif page == "Harvest Entry":
    st.header("🍅 Harvest Log")
    plant = st.selectbox("Select Plant", [p["Name"] for p in st.session_state.data["plants"]])
    date = st.date_input("Harvest Date", datetime.today())
    weight = st.number_input("Harvest Amount (grams)", min_value=0.0, step=1.0)
    if st.button("Log Harvest"):
        save_entry("harvests", {"Plant": plant, "Date": date, "Grams": weight})
        st.success("Harvest recorded.")

# --- Dashboard ---
elif page == "Dashboard":
    st.title("📊 GrowPilot.ai Dashboard")

    plants_df = to_df("plants")
    harvest_df = to_df("harvests")

    if not harvest_df.empty:
        st.subheader("Harvest Timeline")
        harvest_df["Date"] = pd.to_datetime(harvest_df["Date"])
        grouped = harvest_df.groupby("Date")["Grams"].sum().reset_index()
        st.line_chart(grouped.rename(columns={"Grams": "Total Harvest (g)"}).set_index("Date"))

        st.subheader("📈 Harvest Prediction (Linear Forecast)")
        harvest_df = harvest_df.sort_values("Date")
        harvest_df["Days Since Start"] = (harvest_df["Date"] - harvest_df["Date"].min()).dt.days
        model = LinearRegression()
        X = harvest_df[["Days Since Start"]]
        y = harvest_df["Grams"]
        model.fit(X, y)

        future_days = pd.DataFrame({"Days Since Start": range(X["Days Since Start"].max() + 1, X["Days Since Start"].max() + 15)})
        future_predictions = model.predict(future_days)

        fig, ax = plt.subplots()
        ax.plot(harvest_df["Date"], y, label="Actual")
        future_dates = [harvest_df["Date"].min() + pd.Timedelta(days=int(i)) for i in future_days["Days Since Start"]]
        ax.plot(future_dates, future_predictions, label="Forecast", linestyle="--")
        ax.set_title("Harvest Prediction")
        ax.set_ylabel("Grams")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("No harvest data to display yet.")

# --- Export Data ---
elif page == "Export Data":
    st.header("📤 Export Logs")
    for section in st.session_state.data:
        df = to_df(section)
        st.download_button(
            label=f"Download {section.title()} Data",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{section}.csv",
            mime="text/csv"
        )



<style>
body {
    font-family: 'Inter', sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
}
:root {
    --background-color: #f9f9fb;
    --text-color: #1f2937;
    --card-bg: #ffffff;
    --accent-color: #10b981;
    --border-radius: 12px;
}
[data-theme="dark"] {
    --background-color: #111827;
    --text-color: #f9fafb;
    --card-bg: #1f2937;
    --accent-color: #34d399;
}
.card {
    background-color: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
button, .stButton > button {
    border-radius: var(--border-radius);
    background-color: var(--accent-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
}
button:hover {
    opacity: 0.9;
    transition: 0.3s;
}
</style>
