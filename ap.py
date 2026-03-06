import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import psycopg2

#===========================================================
#DATABASE CONNECTION
#===========================================================
def get_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=st.secrets["DB_PORT"],
            sslmode="require"   # REQUIRED for Supabase
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# ==========================================================
# CHECK IF PREDICTION EXISTS
# ==========================================================

def check_existing_prediction(data):

    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT predicted_delay FROM prediction_history
    WHERE year=%s AND month=%s AND carrier=%s AND airport=%s
    AND arr_flights=%s AND arr_del15=%s
    AND carrier_ct=%s AND weather_ct=%s
    AND nas_ct=%s AND security_ct=%s
    AND late_aircraft_ct=%s AND arr_cancelled=%s
    AND arr_diverted=%s
    """

    cur.execute(query,(
        int(data["year"][0]),
        int(data["month"][0]),
        str(data["carrier"][0]),
        str(data["airport"][0]),
        int(data["arr_flights"][0]),
        int(data["arr_del15"][0]),
        float(data["carrier_ct"][0]),
        float(data["weather_ct"][0]),
        float(data["nas_ct"][0]),
        float(data["security_ct"][0]),
        float(data["late_aircraft_ct"][0]),
        int(data["arr_cancelled"][0]),
        int(data["arr_diverted"][0])
    ))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

# ==========================================================
# SAVE PREDICTION TO DATABASE
# ==========================================================

def save_prediction(username, data, prediction):

    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO prediction_history (
        username,year,month,carrier,airport,
        arr_flights,arr_del15,carrier_ct,
        weather_ct,nas_ct,security_ct,
        late_aircraft_ct,arr_cancelled,arr_diverted,
        predicted_delay
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cur.execute(query,(
        username,
        int(data["year"][0]),
        int(data["month"][0]),
        str(data["carrier"][0]),
        str(data["airport"][0]),
        int(data["arr_flights"][0]),
        int(data["arr_del15"][0]),
        float(data["carrier_ct"][0]),
        float(data["weather_ct"][0]),
        float(data["nas_ct"][0]),
        float(data["security_ct"][0]),
        float(data["late_aircraft_ct"][0]),
        int(data["arr_cancelled"][0]),
        int(data["arr_diverted"][0]),
        float(prediction)
    ))

    conn.commit()

    cur.close()
    conn.close()
# ==========================================================
# CONNECTION TEST FUNCTION
# ==========================================================

def test_connection():
    conn = get_connection()

    if conn is None:
        return False

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return True
        return False

    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return False


# ==========================================================
# TEST BUTTON
# ==========================================================

if st.button("🔌 Test Supabase Connection"):
    if test_connection():
        st.success("✅ Supabase Connected Successfully!")
    else:
        st.error("❌ Connection Failed")
# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="AeroInsight Enterprise",
    page_icon="✈️",
    layout="wide"
)

# ==========================================================
# ULTRA PROFESSIONAL CSS
# ==========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }

    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(15px);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0,114,255,0.3);
        text-align:center;
    }

    .login-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 0 40px rgba(0,114,255,0.4);
        text-align:center;
    }

    .stButton>button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ==========================================================
# LOGIN SYSTEM
# ==========================================================
def authenticate_user(username, password):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()
    return user

def create_account(username, password):

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s,%s)",
            (username, password)
        )

        conn.commit()
        return True

    except:
        st.error("Username already exists")

    finally:
        cur.close()
        conn.close()

    return False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():

    st.markdown("<h1 style='text-align:center;'>✈️ AeroInsight</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Enterprise Aviation Intelligence Platform</h4>", unsafe_allow_html=True)

    option = st.radio(
        "Select Option",
        ["Login", "Create Account"],
        horizontal=True
    )

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # LOGIN PAGE
        if option == "Login":

            if st.button("🔐 Secure Login"):

                user = authenticate_user(username, password)

                if user:
                    st.success("Access Granted")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    time.sleep(1)
                    st.rerun()

                else:
                    st.error("Invalid Credentials")

        # CREATE ACCOUNT PAGE
        if option == "Create Account":

            st.subheader("Create New Account")

            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Create Account"):

                if password != confirm_password:
                    st.error("Passwords do not match")

                else:
                    success = create_account(username, password)

                    if success:
                        st.success("Account created successfully! Please login.")

if not st.session_state.logged_in:
    login()
    st.stop()

# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================
st.sidebar.title("✈️ AeroInsight")
page = st.sidebar.radio("Navigation", ["Dashboard", "Prediction"])

# ==========================================================
# LOAD DATA
# ==========================================================
@st.cache_data
def load_data():
    cols_needed = [
        "year","month","arr_flights","arr_del15",
        "carrier_ct","weather_ct","nas_ct","security_ct",
        "late_aircraft_ct","arr_cancelled","arr_diverted",
        "carrier","airport","arr_delay"
    ]

    df = pd.read_csv(
        "flight.csv",
        usecols=cols_needed,
        dtype={
                "year": "Int16",
                "month": "Int8",
                "arr_flights": "Int32",
                "arr_del15": "Int32",
                "carrier_ct": "float32",
                "weather_ct": "float32",
                "nas_ct": "float32",
                "security_ct": "float32",
                "late_aircraft_ct": "float32",
                "arr_cancelled": "Int16",
                "arr_diverted": "Int16",
                "arr_delay": "float32"
            }   
    )

    return df

df = load_data()
df = df.dropna()
df = df[df["arr_flights"] > 0]
# ==========================================================
# FEATURE ENGINEERING
# ==========================================================
le_carrier = LabelEncoder()
le_airport = LabelEncoder()

df["carrier_encoded"] = le_carrier.fit_transform(df["carrier"])
df["airport_encoded"] = le_airport.fit_transform(df["airport"])

y = df["arr_delay"]

X = df[[
    "year","month","arr_flights","arr_del15",
    "carrier_ct","weather_ct","nas_ct","security_ct",
    "late_aircraft_ct","arr_cancelled","arr_diverted",
    "carrier_encoded","airport_encoded"
]]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

@st.cache_resource
def train_model(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=10,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

model = train_model(X_train, y_train)

accuracy = model.score(X_test, y_test)

# ==========================================================
# DASHBOARD
# ==========================================================
if page == "Dashboard":

    st.title("✈️ AeroInsight Enterprise Dashboard")
    st.markdown("### Real-Time Airline Intelligence")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Model Accuracy</h3>
            <h2>{round(accuracy*100,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Delay</h3>
            <h2>{round(df["arr_delay"].mean(),2)} mins</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Model R² Score</h3>
            <h2>{round(accuracy,3)}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Monthly Trend
    st.subheader("📊 Monthly Delay Trend")

    monthly_delay = df.groupby("month")["arr_delay"].mean().reset_index()

    fig_line = px.line(
        monthly_delay,
        x="month",
        y="arr_delay",
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig_line, width='stretch')

    st.markdown("---")

    # Airport Map
    st.subheader("🌍 Global Airport Activity Map")

    if "latitude" in df.columns and "longitude" in df.columns:

        fig_map = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            size="arr_flights",
            hover_name="airport_name",
            zoom=3,
            height=600,
        )

        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(l=0,r=0,t=0,b=0)
        )

        st.plotly_chart(fig_map, width='stretch')

    else:
        st.warning("Dataset must include latitude & longitude columns.")

# ==========================================================
# PREDICTION PAGE
# ==========================================================
elif page == "Prediction":

    st.title("🔮 AI Delay Prediction Engine")

    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox("Year", sorted(df["year"].unique()))
        month = st.selectbox("Month", range(1,13))
        carrier = st.selectbox("Carrier", le_carrier.classes_)
        airport = st.selectbox("Airport", le_airport.classes_)
        late_aircraft_ct = st.number_input("Late Aircraft Count", 0)
        arr_cancelled = st.number_input("Cancelled Flights", 0)
        arr_diverted = st.number_input("Diverted Flights", 0)
    with col2:
        arr_flights = st.number_input("Arrival Flights", 1)
        arr_del15 = st.number_input("Flights Delayed >15 mins", 0)
        carrier_ct = st.number_input("Carrier Delay Count", 0)
        weather_ct = st.number_input("Weather Delay Count", 0)
        nas_ct = st.number_input("NAS Delay Count", 0)
        security_ct = st.number_input("Security Delay Count", 0)
       

    if st.button("🚀 Predict Delay"):

        # Create dataframe for inputs
        input_data = pd.DataFrame({
            "year":[year],
            "month":[month],
            "carrier":[carrier],
            "airport":[airport],
            "arr_flights":[arr_flights],
            "arr_del15":[arr_del15],
            "carrier_ct":[carrier_ct],
            "weather_ct":[weather_ct],
            "nas_ct":[nas_ct],
            "security_ct":[security_ct],
            "late_aircraft_ct":[late_aircraft_ct],
            "arr_cancelled":[arr_cancelled],
            "arr_diverted":[arr_diverted]
        })

        model_input = pd.DataFrame({
            "year":[year],
            "month":[month],
            "arr_flights":[arr_flights],
            "arr_del15":[arr_del15],
            "carrier_ct":[carrier_ct],
            "weather_ct":[weather_ct],
            "nas_ct":[nas_ct],
            "security_ct":[security_ct],
            "late_aircraft_ct":[late_aircraft_ct],
            "arr_cancelled":[arr_cancelled],
            "arr_diverted":[arr_diverted],
            "carrier_encoded":[le_carrier.transform([carrier])[0]],
            "airport_encoded":[le_airport.transform([airport])[0]]
        })

        prediction = model.predict(model_input)[0]

        save_prediction(
            st.session_state.username,
            input_data,
            prediction
        )

        st.success(f"✈️ Estimated Delay: {round(prediction,2)} Minutes")