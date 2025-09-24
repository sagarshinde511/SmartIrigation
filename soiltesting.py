import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# Database credentials
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students1",
    "password": "testStudents@123",
    "database": "u263681140_students1"
}

# Default login credentials
USERNAME = "admin"
PASSWORD = "password"

# Sidebar login
st.sidebar.title("Login")
username = st.sidebar.text_input("Username", value="", placeholder="Enter username")
password = st.sidebar.text_input("Password", type="password", value="", placeholder="Enter password")
login_button = st.sidebar.button("Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if login_button:
    if username == USERNAME and password == PASSWORD:
        st.session_state.authenticated = True
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Invalid Credentials")

# Function to display the home page
def show_home_page():
    st.title("IoT-Based Smart Irrigation System")
    st.image("irrigation.jpeg", use_container_width=True)
    st.write(
        "This project automates irrigation by monitoring soil moisture, temperature, and humidity "
        "using IoT sensors. The collected data optimizes water usage, improving agricultural efficiency."
    )

# If not logged in, show home page and stop execution
if not st.session_state.authenticated:
    show_home_page()
    st.stop()

# Function to fetch latest sensor data
def fetch_latest_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, dateTime, temp, humi, moi, moi2, moi3, moi4 
            FROM Irrigation ORDER BY id DESC LIMIT 1
        """)
        latest_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return latest_data
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to fetch all sensor data
def fetch_all_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT dateTime, temp, humi, moi, moi2, moi3, moi4 
            FROM Irrigation ORDER BY dateTime ASC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(data)
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Main content after login
st.title("IoT Sensor Dashboard")
tabs = st.tabs(["Dashboard", "All Data"])

# Tab 1: Dashboard
with tabs[0]:
    st.subheader("Live Sensor Data")
    latest_data = fetch_latest_data()
    
    if latest_data:
        st.write(f"**Latest Data Timestamp:** {latest_data['dateTime']}")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric(label="Temperature", value=f"{latest_data['temp']}°C")
        with col2:
            st.metric(label="Humidity", value=f"{latest_data['humi']}%")
        with col3:
            st.metric(label="Moisture 1", value=f"{latest_data['moi']}%")
        with col4:
            st.metric(label="Moisture 2", value=f"{latest_data['moi2']}%")
        with col5:
            st.metric(label="Moisture 3", value=f"{latest_data['moi3']}%")
        with col6:
            st.metric(label="Moisture 4", value=f"{latest_data['moi4']}%")
    else:
        st.error("Failed to fetch latest sensor data.")

# Tab 2: All Data
with tabs[1]:
    st.subheader("Past Sensor Data Visualization")
    data = fetch_all_data()
    
    if data is not None and not data.empty:
        st.write("### Sensor Data Trends")
        fig = px.line(
            data.melt(id_vars=['dateTime'], var_name='Sensor', value_name='Value'),
            x='dateTime', y='Value', color='Sensor',
            title='Sensor Data Over Time',
            labels={'Value': 'Sensor Readings', 'dateTime': 'Timestamp'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Raw Data")
        st.dataframe(data)
    else:
        st.error("No data available to display.")
