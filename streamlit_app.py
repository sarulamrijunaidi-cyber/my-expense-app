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
    
    # You can set your own passwords here
    if st.button("Login"):
        if (user == "sarul" and password == "sarul123") or (user == "husband" and password == "pass123"):
            st.session_state.authenticated = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop() # Stops the rest of the app until login

# 3. PERMANENT DATABASE SETUP (With Username Column)
DB_FILE = 'database.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['Username', 'Date', 'Month_Year', 'Item_Name', 'Amount', 'Category']).to_csv(DB_FILE, index=False)

if 'expenses_db' not in st.session_state:
    st.session_state.expenses_db = pd.read_csv(DB_FILE)

# 4. FILTER DATA BY USER
current_user = st.session_state.username
full_db = st.session_state.expenses_db
# This line ensures you only see your specific data
user_data_only = full_db[full_db['Username'] == current_user].copy()

# 5. DASHBOARD CALCULATIONS
user_data_only['Amount'] = pd.to_numeric(user_data_only['Amount'], errors='coerce').fillna(0)
user_data_only['Date'] = pd.to_datetime(user_data_only['Date'], errors='coerce')

current_month_name = datetime.date.today().strftime("%B %Y")
month_total = user_data_only[user_data_only['Month_Year'] == current_month_name]['Amount'].sum()
latest_year_total = user_data_only[user_data_only['Date'].dt.year == 2026]['Amount'].sum()
overall_total = user_data_only['Amount'].sum()

# 6. SIDEBAR DISPLAY
st.sidebar.title(f"👤 Hello, {current_user.capitalize()}")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()
st.sidebar.write(f"Spent in {current_month_name}")
st.sidebar.markdown(f"<h2 style='font-size: 32px; font-weight: bold; margin-top: -15px;'>RM {month_total:,.2f}</h2>", unsafe_allow_html=True)

# 7. ADD ITEM FORM (Saves with Username)
with st.expander("➕ Add New Expense"):
    with st.form("expense_form"):
        date_input = st.date_input("Date", datetime.date.today())
        item_name = st.text_input("Item Name")
        amount_input = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
        category = st.selectbox("Category", ["Food", "Groceries", "Bills", "Self Rewards", "Loans", "Other"])
        submit = st.form_submit_button("Submit")

    if submit and item_name and amount_input > 0:
        new_entry = pd.DataFrame({
            'Username': [current_user], # Tags the entry to the user
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

# 8. HISTORY (Only shows your data)
st.header(f"📝 {current_user.capitalize()}'s History")
st.dataframe(user_data_only.sort_values('Date', ascending=False), use_container_width=True)

# 9. MONTHLY SUMMARY TABLE

    st.subheader("Monthly Spending Summary")

    trend_table = monthly_grouped[['Month_Year', 'Amount']].copy()

    trend_table['Amount'] = trend_table['Amount'].map('RM {:.2f}'.format)

    trend_table.columns = ['Month_Year', 'Total Spent']

    st.table(trend_table)



    # 10. FULL HISTORY ARCHIVE (The New Section You Requested)

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
