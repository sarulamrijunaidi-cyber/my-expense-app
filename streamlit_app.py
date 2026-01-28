import streamlit as st
import pandas as pd
import datetime

# 1. APP CONFIGURATION
st.set_page_config(page_title="Sarul's Expense App", layout="wide")
st.title("📊 Sarul's Expense Tracker")

# 2. DATABASE SETUP
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(
        columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']
    )

# Force numeric for math
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR DASHBOARD - MULTI-LEVEL TRACKING
st.sidebar.header("📍 Dashboard")
df = st.session_state.expenses_db.copy()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Calculations for the 3 Categories
current_month = datetime.date.today().strftime("%B %Y")
latest_month_total = df[df['Month_Year'] == current_month]['Amount'].sum()
latest_year_total = df[df['Date'].dt.year == 2026]['Amount'].sum()
overall_total = df['Amount'].sum()

# Display with RM Currency format
st.sidebar.metric(f"Spent in {current_month}", f"RM {latest_month_total:,.2f}")
st.sidebar.metric("Total for 2026", f"RM {latest_year_total:,.2f}")
st.sidebar.metric("Overall Total", f"RM {overall_total:,.2f}")

st.sidebar.divider()
if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.rerun()

# 4. ADD ITEM FORM
with st.expander("➕ Add New Expense", expanded=False):
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", datetime.date.today())
            item_name = st.text_input("Item Name")
        with col2:
            amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
            category = st.selectbox("Category", [
                "House Rent", "Utilities Bill", "Groceries", "Beverages", 
                "Food", "Self Rewards", "Personal Loan", "Car Loan", 
                "Motorcycle Loan", "Others Bank Loan", "Insurances", "Gift", "Others"
            ])
        submit_button = st.form_submit_button("Submit Expense")

    if submit_button and item_name and amount_input > 0:
        new_entry = pd.DataFrame({
            'Date': [date_input], 'Month_Year': [date_input.strftime("%B %Y")],
            'Item_Name': [item_name], 'Amount': [float(amount_input)], 'Category': [category]
        })
        st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
        st.rerun()

# 5. EDIT & DELETE SECTION
st.header("📝 Expense History (Click to Edit)")

# Editable table: You can change details directly here
edited_df = st.data_editor(
    st.session_state.expenses_db,
    column_config={
        "Amount": st.column_config.NumberColumn("Amount", format="RM %.2f"), # Currency format
    },
    use_container_width=True,
    num_rows="dynamic" # This allows you to delete rows by selecting and pressing 'Delete'
)
st.session_state.expenses_db = edited_df

# Manual Delete Last Entry Button
if not st.session_state.expenses_db.empty:
    if st.button("❌ Delete Last Entry"):
        st.session_state.expenses_db = st.session_state.expenses_db.drop(st.session_state.expenses_db.index[-1])
        st.rerun()

# 6. ANALYTICS
if not st.session_state.expenses_db.empty:
    st.divider()
    st.header("📈 Data Analytics")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("By Category")
        cat_data = st.session_state.expenses_db.groupby('Category')['Amount'].sum()
        st.bar_chart(cat_data, color="#FF4B4B")
            
    with c2:
        st.subheader("Monthly Trend")
        summary = st.session_state.expenses_db.copy()
        summary['Sort_Date'] = pd.to_datetime(summary['Month_Year'], format='%B %Y')
        summary = summary.groupby(['Month_Year', 'Sort_Date'])['Amount'].sum().reset_index()
        summary = summary.sort_values('Sort_Date', ascending=False)
        st.bar_chart(data=summary, x='Month_Year', y='Amount', color="#0072B2")
