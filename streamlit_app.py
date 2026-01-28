import streamlit as st
import pandas as pd
import datetime
import os
import hashlib

# 1. APP CONFIGURATION
st.set_page_config(page_title="My Personal Tracker", page_icon="💰", layout="wide")

# 2. USER DATABASE SETUP
USER_DB = 'users.csv'
if not os.path.exists(USER_DB):
    # Default admin account
    pd.DataFrame([{"Username": "Watie", "Password": "Watie_2020"}], columns=['Username', 'Password']).to_csv(USER_DB, index=False)

def get_users():
    return pd.read_csv(USER_DB)

def add_user(new_user, new_pass):
    df = get_users()
    if new_user in df['Username'].values:
        return False
    new_data = pd.DataFrame([{"Username": new_user, "Password": new_pass}])
    pd.concat([df, new_data], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# 3. LOGIN & REGISTER UI
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("💰 Welcome to Financial Tracker")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            users_df = get_users()
            if ((users_df['Username'] == u) & (users_df['Password'] == p)).any():
                st.session_state.authenticated = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_u = st.text_input("Create Username", key="reg_user")
        new_p = st.text_input("Create Password", type="password", key="reg_pass")
        confirm_p = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register Account"):
            if new_p != confirm_p:
                st.error("Passwords do not match")
            elif len(new_u) < 3:
                st.error("Username too short")
            else:
                if add_user(new_u, new_p):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
    st.stop()

# --- MAIN APP CODE (Only runs after Login) ---
DB_FILE = 'database.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(DB_FILE, index=False)

# Load and Filter Data
full_db = pd.read_csv(DB_FILE)
full_db['Amount'] = pd.to_numeric(full_db['Amount'], errors='coerce').fillna(0)
full_db['Date'] = pd.to_datetime(full_db['Date'], errors='coerce')
user_data = full_db[full_db['Username'] == st.session_state.username].copy()

# Sidebar & Metrics
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

# (Rest of your Dashboard and Form code follows here...)
st.title(f"📊 {st.session_state.username}'s Dashboard")
# ... [Use previous form and table logic here] ...
