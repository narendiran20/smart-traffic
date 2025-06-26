import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Traffic Dashboard", layout="wide")

# 📌 Title
st.title("🚦 Smart Traffic Dashboard")
st.markdown("Monitor and analyze vehicle speed logs with filtering and export options.")

# 📁 Connect to SQLite DB
conn = sqlite3.connect('traffic_data.db')
df = pd.read_sql_query("SELECT * FROM vehicle_log", conn)

# 📆 Format and sort
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
df['Date'] = df['timestamp'].dt.date

# 👁️ Show columns (for debug)
# st.write("Columns:", df.columns.tolist())  # Uncomment to debug

# 🔍 Filter Options
st.sidebar.header("🔎 Filter Logs")

# Date selector
selected_date = st.sidebar.selectbox("📅 Select Date", df['Date'].unique())

# Speed slider
min_speed = int(df['speed'].min())
max_speed = int(df['speed'].max())
selected_speed = st.sidebar.slider("⚡ Speed Range (km/h)", min_value=min_speed, max_value=max_speed, value=(min_speed, max_speed))

# Filter data
filtered_df = df[(df['Date'] == selected_date) & (df['speed'].between(*selected_speed))]

# 🗑️ Clear logs
log_file = "fine_log.txt"
if st.sidebar.button("🗑️ Clear Logs"):
    open(log_file, "w").close()
    st.sidebar.success("Logs cleared!")

# 📋 Show filtered data
st.subheader(f"📄 Vehicle Speed Logs for {selected_date}")
st.dataframe(filtered_df)

# ⬇️ Download CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download CSV",
    data=csv,
    file_name=f"traffic_data_{selected_date}.csv",
    mime='text/csv',
)

# 📈 Speed over Time chart
st.subheader("📈 Speed Over Time")
if not filtered_df.empty:
    st.line_chart(filtered_df.set_index('timestamp')['speed'])

# 📊 Speed Range Pie Chart
st.subheader("📊 Speed Distribution")
labels = ['0–40', '41–60', '61–80', '81+']
bins = [0, 40, 60, 80, 200]
filtered_df['range'] = pd.cut(filtered_df['speed'], bins=bins, labels=labels)

fig, ax = plt.subplots()
filtered_df['range'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, ax=ax)
ax.set_ylabel('')
st.pyplot(fig)

# 📊 Summary Metrics
st.metric("🚨 Overspeeding Vehicles", filtered_df[filtered_df['speed'] > 80].shape[0])
st.metric("⚡ Average Speed", f"{filtered_df['speed'].mean():.2f} km/h")

conn.close()
