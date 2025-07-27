import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor
import contextlib
from contextlib import contextmanager
from backend.log_setup import logger_setup
import os
#%% Global variables
ALLOWED_COLUMNS =["expense_date","amount","category","notes"]
ALLOWED_OPERATORS =[">",">=","<","<=","=","!=","like"]

#%% Logging config
logger=logger_setup("logger_setup","server.log")


#%% Functions

@contextmanager #This decorator will help us to use the cursor object (which execute queries) along all CRUD operations
def get_db_cursor(commit=False): #We will set commit option as false to only commit changes that come from Create Update and Delete operations
    '''
        Description:
            Generator to establish connection with a local MySQL server, and commit changes to databases
        Inputs:
            commit (Bool): Set to False as default, when set to true in Create Update and Delete operations will commit changes to the database    
    '''
    
    #******* Establishing connection
    logger.info(f"Connection attempt...")
    connection = psycopg2.connect(os.getenv("DATABASE_PUBLIC_URL"))

    if connect.status==extensions.STATUS_READY:
        logger.info("Connection result: Success")
    else:
        logger.error("Connection result: Failed")
        raise ConnectionError ("Python was unable to connect to local host")
        
    #****** Setting the cursor object. This will help us execute and extract the results from queries
    cursor = connect.cursor(cursor_factory=RealDictCursor) # Dict option will return results as a python dictionary instead of tuples

    yield cursor # This will work as the generator that will save us code in the rest of the CRUD processes

    #****** Commit changes if needed

    if commit:
        connect.commit()
        logger.info("Changes committed successfully")

    cursor.close()
    connect.close()
    logger.info("Disconnection: Success \n")

def create_record(expense_date,amount,category,notes):
    '''
        Description:
            Function for Create operation in expenses table
        Inputs:
            expense_date (str as yyy-mm-dd): Expense date
            amount(float): Amount of the expense
            category (str): Category of the expense
            notes (str): Descriptive note of the expense 
    '''
    logger.info(f"Function call: create_record")
    #********* Executing the query
    with get_db_cursor(commit=True) as cursor: #This will use the generator and save us the effort to write close and commit in the conding and during the unitary testing
        query='''
            INSERT INTO
                expenses (expense_date,amount,category,notes)
            VALUES
                (%s,%s,%s,%s)
        ''' # %s works as a place holder where we will insert our parammeters
        
        #Try to execute the query. Raise 
        try:
            cursor.execute(query,(expense_date,amount,category,notes)) #We pass all the arguments tu cursor execution
            logger.info(f"Record creation: |date:{expense_date} | amount:{amount} | category:{category} | notes:{notes}| with success")
        except Exception as e:
            logger.error(f"creating record expense date:{expense_date} | amount:{amount} | category:{category} | notes:{notes}. {e}")
            raise RuntimeError(f"Unable to create record. {e}")
    
def retrieve_date(date_retrieval):
    '''
        Description:
            Function used to retrieve information from a certain date from expenses table
        Inputs:
            date_retrieval (str as yyyy-mm-dd): Date to retrieve information
    '''
    logger.info(f"Function call: retrieve_date")
    #********* Executing the query
    with get_db_cursor() as cursor: 
        query='''
            SELECT
                *
            FROM
                expenses
            WHERE
                expense_date=(%s) 
        '''
        #Try to execute the query
        try:
            cursor.execute(query,(date_retrieval,)) #query execution
            results=cursor.fetchall() #Get the query results
            logger.info(f"Data retrieved: date {date_retrieval} with success | results:{len(results)}")
        except Exception as e:
            logger.error(f"Retrieving information for date {date_retrieval} Failed - {e}")
            raise RuntimeError("Error at retrieving date information. Check syntax")
 
    return results


def validate_where_clause(where_dict,operator_dict):
    '''
        Description:
            Function used to validate if the given where clause conditions are valid according to existing column names and possible operators
        Inputs
            where_dict (dictionary): Dictionary to retrieve information based on where conditions. Contains column name and value
            operator_dict (dictionary): Dictionary with operators to perform the custom query between column and value of where dict items.
    '''
    logger.info(f"Where dict received: {where_dict}")
    logger.info(f"Operator dict received: {operator_dict}")

    for key in where_dict.keys():
        if key not in ALLOWED_COLUMNS:
            logger.error("Passing invalid column name in payload")
            raise ValueError(f"Column name not in allowed columns")
        if operator_dict[key] not in ALLOWED_OPERATORS:
            logger.error("Passing invalid operator in payload")
            raise ValueError(f"Operator {operator_dict[key]} not in allowed operators")

def keys_to_remove(in_dict):
    '''
        Description:
            Function to remove all inputs that are None from in_dict
        Inputs:
            in_dict(dictionary): Dictionary to clean
        Outputs:
            in_dict: Dictionary updated
    '''

    keys_to_remove = [key for key, val in in_dict.items() if val is None] #Get the items to remove from the dictionary
    
    for key in keys_to_remove:
        in_dict.pop(key,None)
    
    return in_dict 
def retrieve_custom_query(where_dict,operator_dict):
    '''
        Description:
            Function used to execute a custom query given by user in expenses table. READ ONLY QUERY
        Inputs:
            where_dict (dictionary): Dictionary to retrieve information based on where conditions. Contains column name and value
            operator_dict (dictionary): Dictionary with operators to perform the custom query between column and value of where dict items.
    '''
    logger.info(f"Function call: retrieve_custom_query")

    where_dict=keys_to_remove(where_dict)
    operator_dict=keys_to_remove(operator_dict)

    #******** Validating the where clause conditions
    validate_where_clause(where_dict,operator_dict)

    #******** Forming the query
    where_clause=" And ".join([f"{key} {operator_dict[key]} %s" for key in where_dict.keys()])
    query=f"SELECT * FROM expenses WHERE {where_clause}"
    params=list(where_dict.values())

    #******** Executing the custom query
    with get_db_cursor() as cursor:
        try:
            cursor.execute(query,params)
        except Exception as e:
            logger.error(f"Failed at executing custom query. Check syntax")
            raise RuntimeError (f"Database error {e}")
        results=cursor.fetchall()
        logger.info(f"Data retrieved: Custom query executed with success | results:{len(results)}")

    return results

def update_record(set_dict,where_dict,operator_dict):
    '''
        Description:
            Function to update a record in expenses table
        Inputs:
            set_dict(dictonary): Dictionary with key as column name, and value as new value for column
            where_dict(dictionary): Dictionary containing the mapping for where clause, where key is column name, and value is mapping parammeter 
            operator_dict (dictionary): Dictionary with operators to perform the custom query between column and value of where dict items.
        Returns
            num_records(float): Number of records affected 
    '''    
    logger.info(f"Function call: update_record")
    
    #******** Validating the where clause conditions
    set_dict=keys_to_remove(set_dict)
    where_dict=keys_to_remove(where_dict)
    operator_dict=keys_to_remove(operator_dict)

    validate_where_clause(where_dict,operator_dict)
    
    #******** Form the query
    set_query= ", ".join([f"{key}=%s" for key in set_dict.keys()]) 
    where_clause=" AND ".join([f"{key} {operator_dict[key]} %s" for key in where_dict.keys()])
    query=f"UPDATE expenses SET {set_query} WHERE {where_clause}"
    logger.info(f"Update query {query}")
    #Form the placeholder list
    params=list(set_dict.values())+list(where_dict.values())

    #******** Execute the query
    with get_db_cursor(commit=True) as cursor:
        try:
            cursor.execute(query,params)
            num_records=cursor.rowcount
            logger.info(f"Update: Record updated successfully")
        except Exception as e:
            logger.error(f"Unable to update record. Error {e}")
            raise RuntimeError ("Query syntax error")
    return num_records

def delete_record(where_dict,operator_dict):
    '''
     Description:
        Function to return analytics information of the expenses between a start and end date.
    Inputs:
        start_date (str): Initial date of the date range (format: 'YYYY-MM-DD')
        end_date (str): Final date of the date range (format: 'YYYY-MM-DD')
    Returns:
        total_expenses (list of dict): Expense summary per category (top 5), includes total and percent
        top_expenses (list of dict): Top 5 individual expenses in date range
    ''' 
    logger.info(f"Function call: delete_record")

    #******** Validating the where clause conditions
    where_dict=keys_to_remove(where_dict)
    operator_dict=keys_to_remove(operator_dict)
    validate_where_clause(where_dict,operator_dict)

    #******** Form the query
    where_clause=" AND ".join([f"{key} {operator_dict[key]} %s" for key in where_dict.keys()])
    query=f"DELETE FROM expenses WHERE {where_clause}"

    #Form the placeholder list
    params=list(where_dict.values())

    #******** Execute the query
    with get_db_cursor(commit=True) as cursor:
        try:
            cursor.execute(query,params)
            num_records=cursor.rowcount
            logger.info(f"Record delete: Record deleted successfully")
        except Exception as e:
            logger.error(f"Unable to delete record. Error {e}")
            raise RuntimeError ("Query syntax error")
    return num_records

def expense_summary(start_date,end_date):
    '''
        Description
            Function to return analytics informatation of the expenseses between a start date and an end_date
        Inputs
            start_date(str): Initial date of the date range
            end_date(str): Final date of the date range
        Returns
            total_expenses (dictionary): Expense by category in the date range. Contains Total expenses, and number of expenses
            top_expenses(dictionary): Top 5 expenses in the date range. Contains expense date, total expense, category, notes      
    '''
    logger.info("Function call: Expense analytics")

    #****************************** Summary of expenses
    #Form the query
    query='''
        WITH top_categories AS (
            SELECT 
                category,
                SUM(amount) AS total_expense
            FROM expenses
            WHERE expense_date BETWEEN '2024-01-01' AND '2024-09-05'
            GROUP BY category
            ORDER BY total_expense DESC
            LIMIT 5
        ),
        total_sum AS (
            SELECT SUM(total_expense) AS grand_total FROM top_categories
        )
        SELECT 
            t.category,
            t.total_expense,
            ROUND((t.total_expense * 100 / NULLIF(ts.grand_total, 0))::numeric, 2) AS perc_expense
        FROM top_categories t
        CROSS JOIN total_sum ts
        '''

    #Placeholder for parameters
    params=list([start_date,end_date])

    with get_db_cursor() as cursor:
        try:
            cursor.execute(query,params)
            total_expenses=cursor.fetchall()
            logger.info("Date range retrieved successfuly for analytics")
        except Exception as e:
            logger.error("Failed to retrieve date range for analytics")
            raise RuntimeError("Error retrieving date range")

    #****************************** Top expenses
    #Form the query
    query="SELECT * FROM expenses WHERE expense_date BETWEEN %s AND %s ORDER BY amount  DESC LIMIT 5"

    #Placeholder for parameters
    params=list([start_date,end_date])

    with get_db_cursor() as cursor:
        try:
            cursor.execute(query,params)
            top_expenses=cursor.fetchall()
            logger.info("Date range retrieved successfuly for analytics")
        except Exception as e:
            logger.error("Failed to retrieve date range for analytics")
            raise RuntimeError("Error retrieving date range")

    return total_expenses,top_expenses

#%% Test area
if __name__=="__main__":
    start_date="2024-08-02"
    end_date="2024-08-02"
    results,_=retrieve_date(start_date)
    print(results)
