import streamlit as st
from datetime import date
from datetime import datetime
import requests
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os 

#%% global variables and parameters
OPERATORS = [">", ">=", "<", "<=", "=", "!=", "like"]
FEATURES = ["expense_date", "amount", "category", "notes"]
API_URL = os.getenv("API_URL", "https://sql-crud-app-pythonpostgre-production.up.railway.app")
CATEGORIES=["Food","Rent","Shopping","Entertainment","Other"]
format_date = "%Y-%m-%d" #For datess
#%% Functions for frontend design
def condition_block(section_title: str, key_prefix: str,with_operator=False):
    st.subheader(section_title)
    cols_header = st.columns([1, 1, 2])
    cols_header[0].markdown("<div style='padding-top: 10px; font-weight: bold;'>Feature</div>", unsafe_allow_html=True)
    if with_operator:
        cols_header[1].markdown("<div style='padding-top: 10px; font-weight: bold;'>Operator</div>", unsafe_allow_html=True)
    cols_header[2].markdown("<div style='padding-top: 10px; font-weight: bold;'>Value</div>", unsafe_allow_html=True)

    fixed_fields=["expense_date","amount","category","notes"]

    where_dict = {}
    if with_operator:
        operator_dict={}

    for i, field in enumerate(fixed_fields):
        cols = st.columns([1, 1, 2])
        with cols[0]:
            st.markdown(f"<div style='padding-top: 2.0em'>{field}</div>", unsafe_allow_html=True)
        with cols[1]:
            if with_operator:
                operator = st.selectbox(
                label=f"operator_{i}",
                options=[">", ">=", "<", "<=", "=", "!=", "like"],
                key=f"{key_prefix}_operator_{field}",
                label_visibility="hidden" )    
            else:
                st.markdown(f"<div style='padding-top: 2.0em'>=</div>", unsafe_allow_html=True)
   
        with cols[2]:
            value = st.text_input(
            label=f"value_{i}",
            placeholder="NULL" if i >0 else "yyyy-mm-dd",
            key=f"{key_prefix}_value_{field}",
            label_visibility="hidden"
        )
        if value.strip() != "":
            where_dict[field] = value
            if with_operator:
                operator_dict[field] = operator

    if with_operator:
        return where_dict, operator_dict
    else:
        return where_dict

#%% Frontend design
st.title("Expense track management")
create_tab,update_tab,delete_tab,querie_tab,analytics_tab=st.tabs(["Create Records",
                                                                   "Update Records","Delete Records",
                                                                   "Fetch Records","Analytics"])

                                       #Creating the tab design
#*************************************** UPDATE TAB
with update_tab:
    with st.expander("New values"):
        set_dict = condition_block("New Values", "set",False)
    with st.expander("Where to update"):
        where_dict, where_operators = condition_block("Where to update", "where_update",True)

    #Commit the changes
    if st.button("Commit updates",key="button_update"):

        #Validating date formats for set clause
        if ("expense_date" in set_dict.keys()): 
            if (len(set_dict["expense_date"])<10):
                st.error("Date format invalid for set condition, use yyyy-mm-dd")

        #Validating date format
        if ("expense_date" in where_dict.keys()): 
            if (len(where_dict["expense_date"])<10):
                st.error("Date format invalid for where condition, use yyyy-mm-dd")

        payload={
            "set_info":set_dict,
            "where_info":where_dict,
            "operator_info":where_operators
        }
        response=requests.put(f"{API_URL}/expenses",json=payload)
        if response.status_code==200:
            st.success("Expense updated successfully!")
        else:
            st.error(f"Update failed: {response.status_code}")
            st.write(response.text)

#*************************************** DELETE TAB

with delete_tab:
    where_dict, where_operators = condition_block("Where to delete", "where_delete",True)

    #Commit the changes
    if st.button("Commit deletes",key="commit_deletes"):

        #Validating date format
        if ("expense_date" in where_dict.keys()): 
            if (len(where_dict["expense_date"])<10):
                st.error("Date format invalid for where condition, use yyyy-mm-dd")

        payload={
            "where_info":where_dict,
            "operator_info":where_operators
        }
        response=requests.delete(f"{API_URL}/expenses",json=payload)
        if response.status_code==200:
            st.success("Expenses deleted successfully!")
            st.json(response.json())
        else:
            st.error(f"Delete failed: {response.status_code}")
            st.write(response.text)

#*************************************** CREATE TAB
with create_tab:
    #Date input to create new expenses
    expense_date=st.date_input("Enter date",date(2024,8,1),key="create_date")
    #Creating the headers
    with st.form(key="expense_form"):
        col1,col2,col3=st.columns(3)
        with col1:
            st.subheader("Amount")
        with col2:
            st.subheader("Category")
        with col3:
            st.subheader("Notes")

        #Creating the form to enter expenses (Maximum 5 expenses)
        expenses=[]
        for i in range(5):
            form_col1,form_col2,form_col3=st.columns(3)
            with form_col1:
                amount_input=st.number_input(label="Amount",min_value=0.0,value=0.0,
                                             step=1.0,key=f"amount_{i}")
            with form_col2:
                category_input=st.selectbox(label="Category",options=CATEGORIES,
                                            key=f"category_{i}",placeholder="Category")
            with form_col3:
                notes_input=st.text_input(label="Notes",key=f"notes_{i}",placeholder="Special Notes")
            expenses.append({
                "amount":amount_input,
                "category":category_input,
                "notes":notes_input
            })

        create_button=st.form_submit_button()
        if create_button:
            filtered_expenses= [expense for expense in expenses if expense["amount"]>0]
            payload={
                "expense_date":f"{expense_date.year}-{expense_date.month:02d}-{expense_date.day:02d}",
                "entries":filtered_expenses
            }
            response=requests.post(f"{API_URL}/expenses",json=payload)
            if response.status_code==200:
                st.success("Records created successfully")
            else:
                st.error(f"Record creation failed")
                st.write(response.text)

#*************************************** FETCH RECORDS TAB

with querie_tab:
    with st.expander("Query by date"):
        expense_date_fetch=st.date_input("Enter date",date(2024,8,1),key="fetch_date")
        if st.button("Fetch by date",key="button_date_query"):
            response=requests.get(f"{API_URL}/expenses/fetch_date/{expense_date_fetch}")
            if response.status_code==200:
                st.success("Records by date retrieved successfully")
                data=response.json()
                df=pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.error(f"Error retrieving the date information")
                st.write(response.text)
    
    with st.expander("Custom Query"):
        where_dict,where_operators=condition_block("What to query","where_query",True)
        if st.button("Custom query",key="button_custom_query"):

            #Validating date format
            if ("expense_date" in where_dict.keys()): 
                if (len(where_dict["expense_date"])<10):
                    st.error("Date format invalid for where condition, use yyyy-mm-dd")

            payload={
            "where_info":where_dict,
            "operator_info":where_operators
            }
            response=requests.post(f"{API_URL}/expenses/custom_query",json=payload)
            if response.status_code==200:
                st.success("Custom query executed successfully")
                results=response.json()
                df_results_custom_query=pd.DataFrame(results)
                st.dataframe(df_results_custom_query)
            else:
                st.error("Failed to execute custom query")
                st.write(response.text)

#*************************************** FETCH RECORDS TAB
with analytics_tab:
    start_date=st.date_input("Start Date",value="today",key="start_date_range")
    end_date=st.date_input("End Date",value="today",key="end_date_range")
    payload={
        "start_date":f"{start_date.year}-{start_date.month:02d}-{start_date.day:02d}",
        "end_date":f"{end_date.year}-{end_date.month:02d}-{end_date.day:02d}"
    }
    if st.button(label="Execute Analytics",key="button_analytics"):
        response=requests.post(f"{API_URL}/analytics",json=payload)
        
        if response.status_code==200:
            st.success("Analytics retrieved successfully")
            
            #Retrieve data
            data=response.json()
            expense_summary=pd.DataFrame(data["summary_by_category"])
            expense_summary.columns=["Category","Total expense [UoM]","Percentage [%]"]
            top_expense=pd.DataFrame(data["top_expenses"])
            
            #***********Plotly barchart and top expenses 
            col1,col2=st.columns(2)
            #Plotly
            with col1:
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                
                x=expense_summary["Category"].values,
                y=expense_summary["Total expense [UoM]"].values,
                name="Expense by category",
                marker_color="#19899e",
                ))
                fig1.update_layout(
                title="Total expenses",
                xaxis_title="Category",
                yaxis_title="UoM",
                )
                fig1.update_yaxes(showgrid=False)
                st.plotly_chart(fig1, use_container_width=True)
            #Top expenses
            with col2:
                st.markdown("<div style='height: 31px;'></div>", unsafe_allow_html=True)
                st.markdown("**Top expenses in date range**")
                st.markdown("<div style='height: 31px;'></div>", unsafe_allow_html=True)
                st.dataframe(top_expense,use_container_width=True)

            #Expense summary
            st.markdown("Expense Summary")
            st.dataframe(expense_summary)


        else:
            st.error("Analytics retrieve failed")
