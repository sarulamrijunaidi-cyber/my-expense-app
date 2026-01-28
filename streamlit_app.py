import streamlit as st
import pandas as pd
import datetime
import os

# 1. APP CONFIGURATION
st.set_page_config(page_title="My Personal Tracker", page_icon="💰", layout="wide")

# 2. FILE AND DATA SETUP
USER_DB = 'users.csv'
EXPENSE_DB = 'database.csv'

if not os.path.exists(USER_DB):
    pd.DataFrame(columns=['Username', 'Password']).to_csv(USER_DB, index=False)

if not os.path.exists(EXPENSE_DB):
    pd.DataFrame(columns=['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(EXPENSE_DB, index=False)

# Load and fix missing 'Username' column
expenses_df = pd.read_csv(EXPENSE_DB)
if 'Username' not in expenses_df.columns:
    expenses_df['Username'] = 'Watie'
    expenses_df.to_csv(EXPENSE_DB, index=False)

# 3. LOGIN & REGISTER SYSTEM
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("💰 Welcome to Financial Tracker")
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
                st.success("Account created! Please login.")
    st.stop()

# 4. DASHBOARD CALCULATIONS
current_user = st.session_state.username
user_data = expenses_df[expenses_df['Username'] == current_user].copy()
user_data['Amount'] = pd.to_numeric(user_data['Amount'], errors='coerce').fillna(0)
user_data['Date'] = pd.to_datetime(user_data['Date'], errors='coerce')

current_month = datetime.date.today().strftime("%B %Y")
month_spent = user_data[user_data['Month_Year'] == current_month]['Amount'].sum()
year_total = user_data[user_data['Date'].dt.year == 2026]['Amount'].sum()
overall_total = user_data['Amount'].sum()

# 5. SIDEBAR DISPLAY
st.sidebar.title(f"👤 {current_user}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()

# --- RESTORED BUDGET SECTION ---
st.sidebar.subheader("💰 Monthly Budget")
if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}

current_budget = st.session_state.monthly_budgets.get(f"{current_user}_{current_month}", 0.0)
new_budget = st.sidebar.number_input(f"Set Budget", min_value=0.0, value=float(current_budget))
st.session_state.monthly_budgets[f"{current_user}_{current_month}"] = new_budget

remaining_budget = new_budget - month_spent

# Large Metric Displays
st.sidebar.write(f"Spent in {current_month}")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {month_spent:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.write("Remaining Budget")
display_color = "#FF4B4B" # Red
display_val = f"-RM {abs(remaining_budget):,.2f}" if remaining_budget < 0 else f"RM {remaining_budget:,.2f}"
st.sidebar.markdown(f"<h2 style='color: {display_color}; font-size: 32px; font-weight: bold; margin-top: -15px;'>{display_val}</h2>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.write("Total for 2026")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {year_total:,.2f}</h2>", unsafe_allow_html=True)

st.sidebar.write("Overall Total")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {overall_total:,.2f}</h2>", unsafe_allow_html=True)

# 6. MAIN PAGE FORM
st.title(f"📊 {current_user}'s Tracker")
with st.expander("➕ Add New Expense"):
    with st.form("add_form"):
        d = st.date_input("Date", datetime.date.today())
        item = st.text_input("Item Name")
        amt = st.number_input("Amount (RM)", min_value=0.0)
        cat = st.selectbox("Category", ["Food", "Bills", "Groceries", "Self Rewards", "Other"])
        if st.form_submit_button("Submit"):
            new_row = pd.DataFrame([{
                "Username": current_user, "Date": d, "Month_Year": d.strftime("%B %Y"),
                "Item_Name": item, "Amount": amt, "Category": cat
            }])
            pd.concat([expenses_df, new_row], ignore_index=True).to_csv(EXPENSE_DB, index=False)
            st.success("Saved!")
            st.rerun()

# 7. HISTORY & ANALYTICS
st.header("📝 Recent History")
st.dataframe(user_data.sort_values('Date', ascending=False), use_container_width=True)

if not user_data.empty:
    st.divider()
    st.header("📈 Data Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("By Category")
        st.bar_chart(user_data.groupby('Category')['Amount'].sum(), color="#FF4B4B")
    with c2:
        # Fixed Indentation here
        st.subheader("Monthly Spending Summary")
        summary = user_data.copy()
        summary['Sort_Date'] = pd.to_datetime(summary['Month_Year'], format='%B %Y')
        monthly_grouped = summary.groupby(['Month_Year', 'Sort_Date'])['Amount'].sum().reset_index().sort_values('Sort_Date', ascending=False)
        st.table(monthly_grouped[['Month_Year', 'Amount']])
