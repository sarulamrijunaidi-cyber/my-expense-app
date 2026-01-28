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

# Force Amount to numeric to fix dashboard and chart errors
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR DASHBOARD
st.sidebar.header("Dashboard")
total_spent = st.session_state.expenses_db['Amount'].sum()
st.sidebar.metric("Total Expenses", f"RM {total_spent:.2f}")

if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.rerun()

# 4. ADD ITEM FORM
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form"):
        date_input = st.date_input("Date", datetime.date.today())
        month_year = date_input.strftime("%B %Y")
        item_name = st.text_input("Item Name")
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        
        # YOUR UPDATED CATEGORY LIST
        category = st.selectbox("Category", [
            "House Rent", 
            "Utilities Bill", 
            "Groceries", 
            "Beverages", 
            "Food", 
            "Self Rewards", 
            "Personal Loan", 
            "Car Loan", 
            "Motorcycle Loan", 
            "Others Bank Loan", 
            "Insurances", 
            "Gift", 
            "Others"
        ])
        
        submit_button = st.form_submit_button("Submit")

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

# 6. CATEGORY ANALYTICS
if not st.session_state.expenses_db.empty:
    st.header("Spending Analytics & Percentages")
    chart_df = filtered_df.copy()
    chart_df['Amount'] = pd.to_numeric(chart_df['Amount'], errors='coerce').fillna(0)
    
    cat_totals = chart_df.groupby('Category')['Amount'].sum()
    grand_total = cat_totals.sum()
    
    if grand_total > 0:
        percent_df = pd.DataFrame({
            'Total RM': cat_totals.map('RM {:.2f}'.format),
            'Percentage (%)': ((cat_totals / grand_total) * 100).map('{:.1f}%'.format)
        })
        st.table(percent_df)
        st.bar_chart(cat_totals)

    # 7. MONTHLY TREND (Sorted Newest First)
    st.header("Spending by Month & Year")
    monthly_summary = st.session_state.expenses_db.groupby('Month_Year')['Amount'].sum().reset_index()
    
    # Sorting logic for Month/Year order
    monthly_summary['Sort_Date'] = pd.to_datetime(monthly_summary['Month_Year'], format='%B %Y')
    monthly_summary = monthly_summary.sort_values(by='Sort_Date', ascending=False)
    
    st.bar_chart(data=monthly_summary, x='Month_Year', y='Amount')
    
    trend_table = monthly_summary[['Month_Year', 'Amount']].copy()
    trend_table['Amount'] = trend_table['Amount'].map('RM {:.2f}'.format)
    trend_table.columns = ['Month_Year', 'Total Spent']
    st.table(trend_table)

else:
    st.info("No data available yet.")
