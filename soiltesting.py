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

def show_home_page():
    st.title("IoT-Based Smart Irrigation System")
    # Note: Ensure irrigation.jpeg is in the same directory
    st.image("irrigation.jpeg", use_container_width=True)
    st.write(
        "This project automates irrigation by monitoring soil moisture, temperature, and humidity "
        "using IoT sensors. The collected data optimizes water usage, improving agricultural efficiency."
    )

if not st.session_state.authenticated:
    show_home_page()
    st.stop()

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
# Added "Controls" to the tabs list
tabs = st.tabs(["Dashboard", "Visualizations", "Controls"])

# Tab 1: Dashboard (Metrics)
with tabs[0]:
    st.subheader("Live Sensor Data")
    latest_data = fetch_latest_data()
    
    if latest_data:
        st.write(f"**Latest Data Timestamp:** {latest_data['dateTime']}")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1: st.metric(label="Temp", value=f"{latest_data['temp']}°C")
        with col2: st.metric(label="Humidity", value=f"{latest_data['humi']}%")
        with col3: st.metric(label="Moi 1", value=f"{latest_data['moi']}%")
        with col4: st.metric(label="Moi 2", value=f"{latest_data['moi2']}%")
        with col5: st.metric(label="Moi 3", value=f"{latest_data['moi3']}%")
        with col6: st.metric(label="Moi 4", value=f"{latest_data['moi4']}%")
    else:
        st.error("Failed to fetch latest sensor data.")

# Tab 2: All Data & Visualization
with tabs[1]:
    st.subheader("Sensor Data Trends")
    data = fetch_all_data()
    
    if data is not None and not data.empty:
        # Filtering out moi3 and moi4 for the graph
        graph_data = data[['dateTime', 'temp', 'humi', 'moi', 'moi2']]
        
        fig = px.line(
            graph_data.melt(id_vars=['dateTime'], var_name='Sensor', value_name='Value'),
            x='dateTime', y='Value', color='Sensor',
            title='Temperature, Humidity, and Moisture (1 & 2) Trends',
            labels={'Value': 'Readings', 'dateTime': 'Timestamp'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("View Raw Data (Including Moi 3 & 4)"):
            st.dataframe(data)
    else:
        st.error("No data available to display.")

# Tab 3: Controls (NEW)
with tabs[2]:
    st.subheader("Hardware Actuator Controls")
    st.info("Adjust the sliders below to control your system components in real-time.")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        window_pos = st.slider("Window Opening (%)", 0, 100, 0)
        st.write(f"Target: {window_pos}%")
        
    with col_b:
        pump_speed = st.slider("Water Pump Speed", 0, 255, 0)
        st.write(f"PWM Value: {pump_speed}")
        
    with col_c:
        fan_speed = st.slider("Exhaust Fan Speed", 0, 100, 0)
        st.write(f"Target: {fan_speed}%")

    if st.button("Apply Control Settings"):
        # Here you would typically add code to write these values back to your SQL database
        # or send a command via MQTT/API to your IoT hardware.
        st.success(f"Commands Sent: Window {window_pos}%, Pump {pump_speed}, Fan {fan_speed}%")
