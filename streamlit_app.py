import streamlit as st
import pandas as pd
import datetime

# 1. APP CONFIGURATION
st.set_page_config(page_title="Monthly's Expense App", layout="wide")
st.title("📊 Monthly's Expense Tracker")

# 2. DATABASE SETUP
if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(
        columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']
    )

# 2.1 BUDGET SETUP
if 'monthly_budgets' not in st.session_state:
    st.session_state.monthly_budgets = {}

# Force numeric for calculations
st.session_state.expenses_db['Amount'] = pd.to_numeric(st.session_state.expenses_db['Amount'], errors='coerce').fillna(0)

# 3. SIDEBAR DASHBOARD & BUDGET
st.sidebar.header("📍 Dashboard")

# AUTOMATIC MONTH DETECTION: Detects if it is January, February, etc.
current_month_name = datetime.date.today().strftime("%B %Y")

st.sidebar.subheader("💰 Monthly Budget")
# Current Budget for the detected month
current_budget = st.session_state.monthly_budgets.get(current_month_name, 0.0)
new_budget = st.sidebar.number_input(f"Set Budget for {current_month_name}", min_value=0.0, value=float(current_budget), step=50.0)
st.session_state.monthly_budgets[current_month_name] = new_budget

# NEW: RESET BUDGET BUTTON (Placed here as requested)
if st.sidebar.button(f"🔄 Reset {current_month_name} Budget"):
    st.session_state.monthly_budgets[current_month_name] = 0.0
    st.rerun()

# Calculations
df_sidebar = st.session_state.expenses_db.copy()
df_sidebar['Date'] = pd.to_datetime(df_sidebar['Date'], errors='coerce')

latest_month_total = df_sidebar[df_sidebar['Month_Year'] == current_month_name]['Amount'].sum()
remaining_budget = new_budget - latest_month_total

# Display Metrics
st.sidebar.metric(f"Spent in {current_month_name}", f"RM {latest_month_total:,.2f}")

# --- Remaining Budget (Always Red with Negative Support) ---
st.sidebar.write("Remaining Budget")

# Check if over budget to add the negative sign correctly
if remaining_budget < 0:
    # Use abs() to keep the number positive and manually add the minus sign before RM
    display_budget = f"-RM {abs(remaining_budget):,.2f}"
else:
    display_budget = f"RM {remaining_budget:,.2f}"

# HTML to force the red color and large font
st.sidebar.markdown(
    f"<h2 style='color: #FF4B4B; font-size: 32px; font-weight: bold; margin-top: -15px;'>"
    f"{display_budget}</h2>", 
    unsafe_allow_html=True
)

st.sidebar.divider()
latest_year_total = df_sidebar[df_sidebar['Date'].dt.year == 2026]['Amount'].sum()
overall_total = df_sidebar['Amount'].sum()
st.sidebar.metric("Total for 2026", f"RM {latest_year_total:,.2f}")
st.sidebar.metric("Overall Total", f"RM {overall_total:,.2f}")

if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.expenses_db = pd.DataFrame(columns=['Date', 'Month_Year', 'Item_Name', 'Amount', 'Category'])
    st.session_state.monthly_budgets = {}
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

# 5. LATEST MONTH HISTORY
st.header(f"📝 Latest History ({current_month_name})")
latest_view = st.session_state.expenses_db[st.session_state.expenses_db['Month_Year'] == current_month_name]
st.data_editor(
    latest_view,
    column_config={"Amount": st.column_config.NumberColumn("Amount", format="RM %.2f")},
    use_container_width=True, key="latest_editor"
)

# 6. ANALYTICS & 7. SUMMARY
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
        monthly_grouped = summary.groupby(['Month_Year', 'Sort_Date'])['Amount'].sum().reset_index()
        monthly_grouped = monthly_grouped.sort_values('Sort_Date', ascending=False)
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
