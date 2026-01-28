import streamlit as st
import pandas as pd
import datetime

# 1. APP CONFIGURATION
st.set_page_config(page_title="Sarul's Expense App", layout="wide")
st.title("Sarul's Expense Tracker")

# 2. DATABASE SETUP
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(
        columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']
    )

# THE CRITICAL FIX: Force the Amount column to be numeric right at the start
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR - DASHBOARD TOTAL
st.sidebar.header("Dashboard")

# Calculate total after forcing numeric type to fix the RM 0.00 issue
total_spent = st.session_state.expenses_db['Amount'].sum()
st.sidebar.metric("Total Expenses", f"RM {total_spent:.2f}")

# Reset Button to clear "bad" text data from memory
if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.rerun()

# 4. ADD ITEM FORM (Matching your Page 3 sketch)
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form"):
        date_input = st.date_input("Date", datetime.date.today())
        month_year = date_input.strftime("%B %Y")
        item_name = st.text_input("Item Name")
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        category = st.selectbox("Category", [
            "Water Bill", "House Rent", "Internet Bill", 
            "Groceries", "Foods", "Baverages", "Self Rewards"
        ])
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if item_name and amount_input > 0:
            new_entry = pd.DataFrame({
                'Date': [date_input],
                'Month_Year': [month_year],
                'Item_Name': [item_name],
                'Amount': [float(amount_input)], # Explicitly save as a number
                'Category': [category]
            })
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
            st.success(f"Added {item_name} successfully!")
            st.rerun()

# 5. HISTORY & FILTERS
st.header("Expense History")
unique_months = list(st.session_state.expenses_db['Month_Year'].unique())
month_filter = st.selectbox("Filter by Month", ["All"] + unique_months)

filtered_df = st.session_state.expenses_db
if month_filter != "All":
    filtered_df = filtered_df[filtered_df['Month_Year'] == month_filter]

st.dataframe(filtered_df, use_container_width=True)

# 6. ANALYTICS - THE CORRECT CHART FIX
if not st.session_state.expenses_db.empty:
    st.header("Expenses Analytics")
    
    # Create a clean copy for the chart to prevent AttributeErrors
    chart_df = filtered_df.copy()
    chart_df['Amount'] = pd.to_numeric(chart_df['Amount'], errors='coerce').fillna(0)
    
    # Group data by Category
    chart_data = chart_df.groupby('Category')['Amount'].sum()
    
    # Only show chart if there is actual numerical data
    if not chart_data.empty and chart_data.sum() > 0:
        st.write(f"Spending Breakdown for {month_filter}")
        st.pie_chart(chart_data)
    else:
        st.info("Add an expense with an amount to see the analytics chart.")
else:
    st.info("No data available. Please add an expense above.")
