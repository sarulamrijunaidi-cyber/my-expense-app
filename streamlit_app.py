import streamlit as st
import pandas as pd
import datetime

# 1. APP CONFIGURATION
st.set_page_config(
    page_title="My Personal Tracker", # Changes browser tab name
    page_icon="💰",                  # Changes icon
    layout="wide"
)
st.title("💰 My Financial Tracker") # Big title on the page

# 2. DATABASE SETUP
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(
        columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']
    )

if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}

# Force numeric for math
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. MAIN DASHBOARD & PAYMENT ALERTS
st.title("💰 My Financial Tracker")

st.header("📍 Dashboard Summary")

# --- PAYMENT ALERTS SECTION ---
st.subheader("⚠️ Payment Alerts")
due_dates = {
    "House Rent": 1, 
    "Car Loan": 5, 
    "Motorcycle Loan": 5, 
    "Personal Loan": 7, 
    "Utilities Bill": 10
}
today_day = datetime.date.today().day
alerts_found = False

for category, due_day in due_dates.items():
    if due_day >= today_day and (due_day - today_day) <= 7:
        st.warning(f"Reminder: **{category}** is due on the {due_day}st/th!")
        alerts_found = True
    elif today_day > due_day:
        st.error(f"Alert: **{category}** due date ({due_day}st/th) has passed!")
        alerts_found = True

if not alerts_found:
    st.success("All clear! No urgent payments due.")

st.divider()

# --- METRIC BOXES (Now works correctly) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Spent in {current_month_name}", f"RM {month_total:,.2f}")
with col2:
    st.metric("Total for 2026", f"RM {year_total:,.2f}")
with col3:
    st.metric("Overall Total", f"RM {grand_total:,.2f}")

# 4. SIDEBAR BUDGET
st.sidebar.header("⚙️ Settings")
current_budget = st.session_state.monthly_budgets.get(current_month_name, 0.0)
new_budget = st.sidebar.number_input(f"Set Budget for {current_month_name}", min_value=0.0, value=float(current_budget))
st.session_state.monthly_budgets[current_month_name] = new_budget

remaining_budget = new_budget - month_total
st.sidebar.write("Remaining Budget")
color = "#FF4B4B" # Red
display_val = f"-RM {abs(remaining_budget):,.2f}" if remaining_budget < 0 else f"RM {remaining_budget:,.2f}"
st.sidebar.markdown(f"<h2 style='color: {color}; font-weight: bold;'>{display_val}</h2>", unsafe_allow_html=True)

# 4. ADD ITEM FORM
with st.expander("➕ Add New Expense"):
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", datetime.date.today())
            item_name = st.text_input("Item Name")
        with col2:
            amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
            category = st.selectbox("Category", ["House Rent", "Utilities Bill", "Groceries", "Beverages", "Food", "Self Rewards", "Personal Loan", "Car Loan", "Motorcycle Loan", "Credit Card", "Others Bank Loan", "Insurances", "Gift", "Others"])
        if st.form_submit_button("Submit Expense") and item_name and amount_input > 0:
            new_entry = pd.DataFrame({'Date': [date_input], 'Month_Year': [date_input.strftime("%B %Y")], 'Item_Name': [item_name], 'Amount': [float(amount_input)], 'Category': [category]})
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_entry], ignore_index=True)
            st.rerun()

# 5. HISTORY TABLE (EDITABLE)
st.header(f"📝 Latest History ({current_month_name})")
latest_view = st.session_state.expenses_db[st.session_state.expenses_db['Month_Year'] == current_month_name]
st.data_editor(latest_view, column_config={"Amount": st.column_config.NumberColumn("Amount", format="RM %.2f")}, use_container_width=True)

# 6. ANALYTICS & 7. SUMMARY
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

# 7. MONTHLY SUMMARY TABLE
    st.subheader("Monthly Spending Summary")
    trend_table = monthly_grouped[['Month_Year', 'Amount']].copy()
    trend_table['Amount'] = trend_table['Amount'].map('RM {:.2f}'.format)
    trend_table.columns = ['Month_Year', 'Total Spent']
    st.table(trend_table)

    # 8. FULL HISTORY ARCHIVE (The New Section You Requested)
    st.divider()
    st.header("📂 Full Expense Archive")
    
    # Selection for Year and Month
    all_years = sorted(df_sidebar['Date'].dt.year.unique(), reverse=True)
    selected_year = st.selectbox("Select Year to View", all_years)
    
    # Filter for the selected year
    year_data = st.session_state.expenses_db.copy()
    year_data['Date'] = pd.to_datetime(year_data['Date'])
    filtered_year_df = year_data[year_data['Date'].dt.year == selected_year]
    
    # Selection for Month based on that year
    available_months = ["All"] + list(filtered_year_df['Month_Year'].unique())
    selected_month = st.selectbox(f"Select Month in {selected_year}", available_months)
    
    final_archive_df = filtered_year_df
    if selected_month != "All":
        final_archive_df = filtered_year_df[filtered_year_df['Month_Year'] == selected_month]
    
    # Display the final filtered archive
    st.dataframe(
        final_archive_df.sort_values('Date', ascending=False), 
        use_container_width=True,
        column_config={"Amount": st.column_config.NumberColumn("Amount", format="RM %.2f")}
    )

else:
    st.info("No data available yet.")
