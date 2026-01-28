import streamlit as st
import pandas as pd
import datetime
import os

# 1. APP CONFIGURATION
st.set_page_config(
    page_title="My Personal Tracker", 
    page_icon="💰", 
    layout="wide"
)
st.title("💰 My Financial Tracker")

# 2. PERMANENT DATABASE SETUP
DB_FILE = 'database.csv'

# Create file if it doesn't exist
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(DB_FILE, index=False)

# Load data into memory
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.read_csv(DB_FILE)

# 2.1 BUDGET & NUMERIC SETUP
if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}

# Ensure Amount is numeric for math
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR DASHBOARD & BUDGET
st.sidebar.header("📍 Dashboard")
current_month_name = datetime.date.today().strftime("%B %Y")

st.sidebar.subheader("💰 Monthly Budget")
current_budget = st.session_state.monthly_budgets.get(current_month_name, 0.0)
new_budget = st.sidebar.number_input(f"Set Budget for {current_month_name}", min_value=0.0, value=float(current_budget), step=50.0)
st.session_state.monthly_budgets[current_month_name] = new_budget

if st.sidebar.button(f"🔄 Reset {current_month_name} Budget"):
    st.session_state.monthly_budgets[current_month_name] = 0.0
    st.rerun()

# --- CRITICAL CALCULATIONS (Must be before Display) ---
df_sidebar = st.session_state.expenses_db.copy()
df_sidebar['Date'] = pd.to_datetime(df_sidebar['Date'], errors='coerce')

# Monthly Spending
latest_month_total = df_sidebar[df_sidebar['Month_Year'] == current_month_name]['Amount'].sum()

# Remaining Budget
remaining_budget = new_budget - latest_month_total

# Year & Overall Totals (Fixes NameError)
latest_year_total = df_sidebar[df_sidebar['Date'].dt.year == 2026]['Amount'].sum()
overall_total = df_sidebar['Amount'].sum()

# --- LARGE FONT DISPLAY SECTION ---

# 1. Spent in Month
st.sidebar.write(f"Spent in {current_month_name}")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {latest_month_total:,.2f}</h2>", unsafe_allow_html=True)

# 2. Remaining Budget (Red Color)
st.sidebar.write("Remaining Budget")
display_budget = f"-RM {abs(remaining_budget):,.2f}" if remaining_budget < 0 else f"RM {remaining_budget:,.2f}"
st.sidebar.markdown(f"<h2 style='color: #FF4B4B; font-size: 32px; font-weight: bold; margin-top: -15px;'>{display_budget}</h2>", unsafe_allow_html=True)

st.sidebar.divider()

# 3. Total for 2026
st.sidebar.write("Total for 2026")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {latest_year_total:,.2f}</h2>", unsafe_allow_html=True)

# 4. Overall Total
st.sidebar.write("Overall Total")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {overall_total:,.2f}</h2>", unsafe_allow_html=True)

# Reset Button
if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.session_state.expenses_db.to_csv(DB_FILE, index=False) # Clear permanent file
    st.rerun()

# 4. ADD ITEM FORM
with st.expander("➕ Add New Expense"):
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", datetime.date.today())
            item_name = st.text_input("Item Name")
        with col2:
            amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
            category = st.selectbox("Category", ["House Rent", "Utilities Bill", "Groceries", "Beverages", "Food", "Self Rewards", "Personal Loan", "Car Loan", "Motorcycle Loan", "Others Bank Loan", "Insurances", "Gift", "Others"])
        submit_button = st.form_submit_button("Submit Expense")

    if submit_button and item_name and amount_input > 0:
        new_entry = pd.DataFrame({
            'Date': [date_input], 'Month_Year': [date_input.strftime("%B %Y")], 
            'Item_Name': [item_name], 'Amount': [float(amount_input)], 'Category': [category]
        })
        # Update Memory & CSV
        st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
        st.session_state.expenses_db.to_csv(DB_FILE, index=False)
        st.success("Saved permanently!")
        st.rerun()

# 5. HISTORY & ANALYTICS
st.header(f"📝 Latest History ({current_month_name})")
latest_view = st.session_state.expenses_db[st.session_state.expenses_db['Month_Year'] == current_month_name]
st.data_editor(latest_view, use_container_width=True, key="latest_editor")

if not st.session_state.expenses_db.empty:
    st.divider()
    st.header("📈 Data Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("By Category")
        st.bar_chart(st.session_state.expenses_db.groupby('Category')['Amount'].sum(), color="#FF4B4B")
    with c2:
        st.subheader("Monthly Trend")
        summary = st.session_state.expenses_db.copy()
        summary['Sort_Date'] = pd.to_datetime(summary['Month_Year'], format='%B %Y')
        monthly_grouped = summary.groupby(['Month_Year', 'Sort_Date'])['Amount'].sum().reset_index().sort_values('Sort_Date', ascending=False)
        st.bar_chart(data=monthly_grouped, x='Month_Year', y='Amount', color="#0072B2")
