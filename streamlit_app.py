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

# Force Amount to numeric to prevent calculation errors
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR DASHBOARD
st.sidebar.header("📍 Dashboard")
total_spent = st.session_state.expenses_db['Amount'].sum()
st.sidebar.metric("Total Expenses", f"RM {total_spent:.2f}")

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
        
        month_year = date_input.strftime("%B %Y")
        submit_button = st.form_submit_button("Submit Expense")

    if submit_button:
        if item_name and amount_input > 0:
            new_entry = pd.DataFrame({
                'Date': [date_input],
                'Month_Year': [month_year],
                'Item_Name': [item_name],
                'Amount': [float(amount_input)],
                'Category': [category]
            })
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
            st.success(f"Successfully added {item_name}!")
            st.rerun()

# 5. HISTORY TABLE
st.header("📝 Expense History")
st.dataframe(st.session_state.expenses_db, use_container_width=True)

# 6. ATTRACTIVE & COMPACT ANALYTICS
if not st.session_state.expenses_db.empty:
    st.divider()
    st.header("📈 Data Analytics")
    
    # Create two small columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    chart_df = st.session_state.expenses_db.copy()
    
    with chart_col1:
        st.subheader("Category Totals")
        cat_totals = chart_df.groupby('Category')['Amount'].sum()
        # Different colors for each category to make it attractive
        st.bar_chart(cat_totals, color="#FF4B4B") 
            
    with chart_col2:
        st.subheader("Monthly Trend")
        # Sort months newest first
        summary = chart_df.groupby('Month_Year')['Amount'].sum().reset_index()
        summary['Sort_Date'] = pd.to_datetime(summary['Month_Year'], format='%B %Y')
        summary = summary.sort_values(by='Sort_Date', ascending=False)
        st.bar_chart(data=summary, x='Month_Year', y='Amount', color="#0072B2")

    # Small Percentage Table
    st.subheader("Spending Breakdown (%)")
    grand_total = cat_totals.sum()
    if grand_total > 0:
        percent_df = pd.DataFrame({
            'Total RM': cat_totals.map('RM {:.2f}'.format),
            'Percentage (%)': ((cat_totals / grand_total) * 100).map('{:.1f}%'.format)
        })
        st.table(percent_df)
else:
    st.info("Add expenses to see your analytics dashboard!")
