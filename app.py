import calendar
from datetime import datetime

import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import json 

import main as db 
print(dir(db)) 


incomes = ["Salary", "Business", "Investments", "Other Income"]
expenses = ["Rent", "Utilities", "Groceries", "Car", "Entertainment", "Other Expenses"]
currency = "INR(₹)"
page_title = "Personal Finance Tracker"
page_icon = ":money_with_wings:"
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)


years = [datetime.today().year - i for i in range(5)]  
months = list(calendar.month_name[1:])

def get_all_periods():
    items = db.fetch_all_periods()
    print("Extracted periods:", items)
    return items


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Navbar
selected = option_menu(
    menu_title=None,
    options=["Enter Data", "Stored Data"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

# Input Section
if selected == "Enter Data":    
    st.header(f"Enter Data in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")
        "---"
        
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comments"):
            comment = st.text_area(" ", placeholder="Add any comments or notes here...")
            
        "---"
        submitted = st.form_submit_button("Submit")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            income = {income: st.session_state[income] for income in incomes}
            expense = {expense: st.session_state[expense] for expense in expenses}  # Changed variable name
            db.insert_period(period, income, expense, comment)
            st.success(f"Data for {st.session_state['month']} {st.session_state['year']} submitted successfully!")

# Plot Stored Data
if selected == "Stored Data":
    st.header("Stored Data")    
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            period_data = db.get_period(period)
            
            if period_data:
                comment = period_data["comment"]
                incomes = period_data["incomes"]
                expenses = period_data["expenses"]

           
                if not isinstance(incomes, dict):
                    st.warning("Warning: Income data is not in the expected format.")
                    incomes = {}

                if not isinstance(expenses, dict):
                    st.warning("Warning: Expense data is not in the expected format.")
                    expenses = {}

                total_income = sum(incomes.values())  
                total_expenses = sum(expenses.values())  
                remaining_budget = total_income - total_expenses  

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{currency} {total_income}")
                col2.metric("Total Expenses", f"{currency} {total_expenses}")
                col3.metric("Remaining Budget", f"{currency} {remaining_budget}")
                st.text(f"Comment: {comment}")
                
                income_categories = list(incomes.keys())
                income_values = list(incomes.values())

                income_fig = go.Figure(data=[go.Pie(labels=income_categories, values=income_values, hole=0.3, marker=dict(colors=['#FF9999','#66B3FF','#99FF99','#FFCC99']))])
                income_fig.update_layout(title="Income Distribution", template="plotly_dark")
                st.plotly_chart(income_fig)

                # Pie Chart for Expenses
                expense_categories = list(expenses.keys())
                expense_values = list(expenses.values())

                expense_fig = go.Figure(data=[go.Pie(labels=expense_categories, values=expense_values, hole=0.3, marker=dict(colors=['#FF6666','#66FF66','#FFCC00','#FF99FF','#66B3FF','#FF9999']))])
                expense_fig.update_layout(title="Expense Distribution", template="plotly_dark")
                st.plotly_chart(expense_fig)
            else:
                st.error("No data found for the selected period.")


       
