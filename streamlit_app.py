import streamlit as st
import pandas as pd
import datetime
import os

# 1. APP CONFIGURATION
st.set_page_config(page_title="My Personal Tracker", page_icon="💰", layout="wide")

# 2. FILE AND DATA SETUP
USER_DB = 'users.csv'
EXPENSE_DB = 'database.csv'

# Ensure Users file exists
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=['Username', 'Password']).to_csv(USER_DB, index=False)

# Ensure Expense file exists
if not os.path.exists(EXPENSE_DB):
    pd.DataFrame(columns=['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(EXPENSE_DB, index=False)

# Load data and fix missing 'Username' column if needed
expenses_df = pd.read_csv(EXPENSE_DB)
if 'Username' not in expenses_df.columns:
    expenses_df['Username'] = 'Watie' # Assign old data to Watie by default
    expenses_df.to_csv(EXPENSE_DB, index=False)

# 3. LOGIN & REGISTER SYSTEM
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("💰 Financial Tracker")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            users = pd.read_csv(USER_DB)
            if ((users['Username'] == u) & (users['Password'] == p)).any():
                st.session_state.authenticated = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_u = st.text_input("Choose Username", key="reg_u")
        new_p = st.text_input("Choose Password", type="password", key="reg_p")
        if st.button("Create Account"):
            users = pd.read_csv(USER_DB)
            if new_u in users['Username'].values:
                st.error("Username already taken")
            elif new_u and new_p:
                new_user = pd.DataFrame([{"Username": new_u, "Password": new_p}])
                pd.concat([users, new_user], ignore_index=True).to_csv(USER_DB, index=False)
                st.success("Account created! You can now login.")
    st.stop()

# 4. DASHBOARD (Only runs after Login)
current_user = st.session_state.username
# Filter only the current user's data
user_data = expenses_df[expenses_df['Username'] == current_user].copy()
user_data['Amount'] = pd.to_numeric(user_data['Amount'], errors='coerce').fillna(0)

# Sidebar & Totals
st.sidebar.title(f"👤 {current_user}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

current_month = datetime.date.today().strftime("%B %Y")
month_spent = user_data[user_data['Month_Year'] == current_month]['Amount'].sum()

st.sidebar.write(f"Spent in {current_month}")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {month_spent:,.2f}</h2>", unsafe_allow_html=True)

# 5. ADD EXPENSE
st.title(f"📊 {current_user}'s Tracker")
with st.expander("➕ Add New Expense"):
    with st.form("add_form"):
        d = st.date_input("Date", datetime.date.today())
        item = st.text_input("Item Name")
        amt = st.number_input("Amount (RM)", min_value=0.0)
        cat = st.selectbox("Category", ["Food", "Bills", "Others"])
        if st.form_submit_button("Submit"):
            new_row = pd.DataFrame([{
                "Username": current_user, "Date": d, "Month_Year": d.strftime("%B %Y"),
                "Item_Name": item, "Amount": amt, "Category": cat
            }])
            pd.concat([expenses_df, new_row], ignore_index=True).to_csv(EXPENSE_DB, index=False)
            st.success("Saved!")
            st.rerun()

# 6. HISTORY
st.header("📝 Recent History")
st.dataframe(user_data.sort_values('Date', ascending=False), use_container_width=True)
