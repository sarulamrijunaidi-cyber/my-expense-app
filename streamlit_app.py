import streamlit as st
import pandas as pd
import datetime
import os

# 1. APP CONFIGURATION
st.set_page_config(page_title="My Personal Tracker", page_icon="💰", layout="wide")

# 2. LOGIN SYSTEM
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login to Tracker")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Pre-set accounts for you and your husband
    if st.button("Login"):
        if (user == "sarul" and password == "sarul123") or (user == "husband" and password == "pass123"):
            st.session_state.authenticated = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# 3. PERMANENT DATABASE SETUP (With Username Support)
DB_FILE = 'database.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(DB_FILE, index=False)

if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.read_csv(DB_FILE)

# 4. FILTER DATA BY USER
current_user = st.session_state.username
full_db = st.session_state.expenses_db.copy()
full_db['Amount'] = pd.to_numeric(full_db['Amount'], errors='coerce').fillna(0)
full_db['Date'] = pd.to_datetime(full_db['Date'], errors='coerce')

# This line ensures privacy: you only see YOUR data
user_data_only = full_db[full_db['Username'] == current_user].copy()

# 5. CRITICAL CALCULATIONS (Fixes NameError)
current_month_name = datetime.date.today().strftime("%B %Y")
month_total = user_data_only[user_data_only['Month_Year'] == current_month_name]['Amount'].sum()
latest_year_total = user_data_only[user_data_only['Date'].dt.year == 2026]['Amount'].sum()
overall_total = user_data_only['Amount'].sum()

# 6. SIDEBAR DASHBOARD
st.sidebar.title(f"👤 Hello, {current_user.capitalize()}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()

# Set Budget Section
if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}
current_budget = st.session_state.monthly_budgets.get(current_month_name, 0.0)
new_budget = st.sidebar.number_input(f"Set Budget for {current_month_name}", min_value=0.0, value=float(current_budget))
st.session_state.monthly_budgets[current_month_name] = new_budget

remaining_budget = new_budget - month_total

# Large Displays
st.sidebar.write(f"Spent in {current_month_name}")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {month_total:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.write("Remaining Budget")
display_budget = f"-RM {abs(remaining_budget):,.2f}" if remaining_budget < 0 else f"RM {remaining_budget:,.2f}"
st.sidebar.markdown(f"<h2 style='color: #FF4B4B; font-size: 32px; font-weight: bold; margin-top: -15px;'>{display_budget}</h2>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.write("Total for 2026")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {latest_year_total:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.write("Overall Total")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {overall_total:,.2f}</h2>", unsafe_allow_html=True)

# 7. MAIN PAGE: ADD EXPENSE
st.title("💰 My Financial Tracker")
with st.expander("➕ Add New Expense"):
    with st.form("expense_form"):
        date_input = st.date_input("Date", datetime.date.today())
        item_name = st.text_input("Item Name")
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        category = st.selectbox("Category", ["Food", "Groceries", "Bills", "Self Rewards", "Loans", "Other"])
        submit = st.form_submit_button("Submit")

    if submit and item_name and amount_input > 0:
        new_entry = pd.DataFrame({
            'Username': [current_user],
            'Date': [date_input], 
            'Month_Year': [date_input.strftime("%B %Y")], 
            'Item_Name': [item_name], 
            'Amount': [float(amount_input)], 
            'Category': [category]
        })
        st.session_state.expenses_db = pd.concat([full_db, new_entry], ignore_index=True)
        st.session_state.expenses_db.to_csv(DB_FILE, index=False)
        st.success("Saved to your account!")
        st.rerun()

# 8. HISTORY & ANALYTICS
st.header(f"📝 {current_user.capitalize()}'s History")
st.dataframe(user_data_only.sort_values('Date', ascending=False), use_container_width=True)

if not user_data_only.empty:
    st.divider()
    st.header("📈 Data Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("By Category")
        st.bar_chart(user_data_only.groupby('Category')['Amount'].sum(), color="#FF4B4B")
    with c2:
        st.subheader("Monthly Spending Summary") # Fixed Indentation here
        summary = user_data_only.copy()
        summary['Sort_Date'] = pd.to_datetime(summary['Month_Year'], format='%B %Y')
        monthly_grouped = summary.groupby(['Month_Year', 'Sort_Date'])['Amount'].sum().reset_index().sort_values('Sort_Date', ascending=False)
        st.table(monthly_grouped[['Month_Year', 'Amount']])
