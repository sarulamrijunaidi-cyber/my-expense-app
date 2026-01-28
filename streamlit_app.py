import streamlit as st
import pandas as pd
import datetime

# 1. APP CONFIGURATION
st.set_page_config(page_title="Sarul's Expense App", layout="centered")
st.title("Sarul's Expense Tracker")

# 2. DATABASE SETUP
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(
        columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']
    )

# FORCE CONVERSION: This fixes the RM 0.00 error
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR - DASHBOARD TOTAL (Like Page 2 of your sketch)
# Force the Amount column to be numeric so the math works
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce')
total_spent = st.session_state.expenses_db['Amount'].sum()
st.sidebar.metric("Total Expenses", f"RM {total_spent:.2f}")
# Button to wipe out old "text" data
if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.rerun()

# 4. ADD ITEM FORM (Matching your Page 3 sketch)
with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form"):
        # Date input without time
        date_input = st.date_input("Date", datetime.date.today())
        
        # Automatic Month_Year calculation so you don't have to type it
        month_year = date_input.strftime("%B %Y")
        
        item_name = st.text_input("Item Name (e.g., Chicken, TNB)")
        amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        
        # Category Dropdown
        category = st.selectbox("Category", [
            "Water Bill", "House Rent", "Internet Bill", 
            "Groceries", "Foods", "Baverages", "Self Rewards"
        ])
        
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if item_name and amount > 0:
            new_entry = pd.DataFrame({
                'Date': [date_input],
                'Month_Year': [month_year],
                'Item_Name': [item_name],
                'Amount': [float(amount)], # This ensures it is a number
                'Category': [category]
            })
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
            st.success(f"Added {item_name} successfully!")
        else:
            st.warning("Please enter an item name and amount.")

# 5. HISTORY & FILTERS (Matching your Page 4 sketch)
st.header("Expense History")
month_filter = st.selectbox("Filter by Month", ["All"] + list(st.session_state.expenses_db['Month_Year'].unique()))

filtered_df = st.session_state.expenses_db
if month_filter != "All":
    filtered_df = filtered_df[filtered_df['Month_Year'] == month_filter]

st.dataframe(filtered_df, use_container_width=True)

# 6. ANALYTICS (Matching your Page 5 sketch)
if not st.session_state.expenses_db.empty:
    st.header("Expenses Analytics")
    # Only use data where Amount is a valid number
    chart_df = filtered_df.dropna(subset=['Amount'])
    chart_data = chart_df.groupby('Category')['Amount'].sum()
    
    if not chart_data.empty:
        st.write(f"Spending Breakdown for {month_filter}")
        st.pie_chart(chart_data)
else:
    st.info("No data available yet. Please add an expense to see analytics.") 
