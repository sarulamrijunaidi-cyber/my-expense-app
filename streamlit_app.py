import streamlit as st
import pandas as pd
import datetime
import os

# 1. APP CONFIGURATION
st.set_page_config(page_title="Personal Tracker", page_icon="💰", layout="wide")

# 2. FILE AND DATA SETUP
USER_DB = 'users.csv'
EXPENSE_DB = 'database.csv'

# Initialize files if they don't exist
for file, cols in [(USER_DB, ['Username', 'Password']), (EXPENSE_DB, ['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])]:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)

# 3. LOGIN & REGISTER SYSTEM
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("💰 Financial Tracker")
    t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
    with t1:
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
    with t2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users = pd.read_csv(USER_DB)
            if new_u in users['Username'].values:
                st.error("Username taken")
            elif new_u and new_p:
                pd.concat([users, pd.DataFrame([{"Username": new_u, "Password": new_p}])], ignore_index=True).to_csv(USER_DB, index=False)
                st.success("Account created!")
    st.stop()

# 4. DASHBOARD CALCULATIONS (The Multi-User Fix)
current_user = st.session_state.username

# Load ALL data but FILTER immediately
full_db = pd.read_csv(EXPENSE_DB) 
full_db['Amount'] = pd.to_numeric(full_db['Amount'], errors='coerce').fillna(0)
full_db['Date'] = pd.to_datetime(full_db['Date'], errors='coerce')

# THIS IS THE KEY: Filter data for ONLY this user
user_data = full_db[full_db['Username'] == current_user].copy()

# Calculate totals using ONLY user_data
current_month = datetime.date.today().strftime("%B %Y")
month_spent = user_data[user_data['Month_Year'] == current_month]['Amount'].sum()
year_total = user_data[user_data['Date'].dt.year == 2026]['Amount'].sum()
overall_total = user_data['Amount'].sum() # Now shows 0.00 for Haslina

# 5. SIDEBAR DISPLAY
st.sidebar.title(f"👤 {current_user}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("💰 Budgeting")
if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}

# User-specific budget storage
budget_key = f"{current_user}_{current_month}"
current_budget = st.session_state.monthly_budgets.get(budget_key, 0.0)
new_budget = st.sidebar.number_input("Set Monthly Budget", min_value=0.0, value=float(current_budget))
st.session_state.monthly_budgets[budget_key] = new_budget

# FIX: Calculate remaining_budget BEFORE line 90 display
remaining_budget = new_budget - month_spent

st.sidebar.write(f"Spent ({current_month})")
st.sidebar.markdown(f"<h2 style='font-size: 30px;'>RM {month_spent:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.write("Remaining")
color = "#FF4B4B" if remaining_budget < 0 else "#FFFFFF"
st.sidebar.markdown(f"<h2 style='color: {color}; font-size: 30px;'>RM {remaining_budget:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.write("Total for 2026")
st.sidebar.markdown(f"<h2 style='font-size: 30px;'>RM {year_total:,.2f}</h2>", unsafe_allow_html=True)
st.sidebar.write("Overall Total")
st.sidebar.markdown(f"<h2 style='font-size: 30px;'>RM {overall_total:,.2f}</h2>", unsafe_allow_html=True)

# 6. MAIN PAGE FORM
st.title(f"📊 {current_user}'s Dashboard")
with st.expander("➕ Add New Entry"):
    with st.form("add_form"):
        d = st.date_input("Date", datetime.date.today())
        item = st.text_input("Item")
        amt = st.number_input("Amount (RM)", min_value=0.0)
        cat = st.selectbox("Category", ["Food", "Groceries", "Utilities", "Rent", "Other"])
        if st.form_submit_button("Submit"):
            new_row = pd.DataFrame([{"Username": current_user, "Date": d, "Month_Year": d.strftime("%B %Y"), "Item_Name": item, "Amount": amt, "Category": cat}])
            pd.concat([full_db, new_row], ignore_index=True).to_csv(EXPENSE_DB, index=False)
            st.success("Saved!")
            st.rerun()

# 7. HISTORY & DELETE
st.header("📝 Recent History")
edited_df = st.data_editor(user_data[user_data['Month_Year'] == current_month], use_container_width=True, num_rows="dynamic")

if st.button("💾 Save Changes"):
    # Re-combine other users' data with this user's new data
    other_users = full_db[full_db['Username'] != current_user]
    pd.concat([other_users, edited_df], ignore_index=True).to_csv(EXPENSE_DB, index=False)
    st.success("Updated!")
    st.rerun()

# 8. ARCHIVE FIX
st.divider()
st.header("📂 Archive")
valid_years = user_data['Date'].dt.year.dropna().unique()
if len(valid_years) > 0:
    sel_year = st.selectbox("Year", sorted(valid_years.astype(int), reverse=True))
    sel_month = st.selectbox("Month", sorted(user_data[user_data['Date'].dt.year == sel_year]['Month_Year'].unique()))
    st.dataframe(user_data[(user_data['Date'].dt.year == sel_year) & (user_data['Month_Year'] == sel_month)], use_container_width=True)
else:
    st.info("No data yet.")
