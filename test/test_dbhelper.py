from backend import db_helper_postgre
import pytest
import math
import datetime

#%% CREATE TESTING
def test_create_record():
    '''
        Unitary testing for creating a new record. Creates a record for a non existing date in the table, and checks result 
    '''
    date="2025-07-12"
    
    #Cleaning leftovers from possible previous runs
    db_helper_postgre.delete_record({"expense_date": date}, {"expense_date": "="})

    results=db_helper_postgre.retrieve_date(date)

    db_helper_postgre.create_record("2025-07-12",100,"Food","This is a new record")
    results=db_helper_postgre.retrieve_date("2025-07-12")
    assert results[0]["expense_date"]==datetime.date(2025,7,12)
    assert results[0]["amount"]==100
    assert results[0]["category"]=="Food"
    assert results[0]["notes"]=="This is a new record"

def test_read_date():
    '''
        Unitary testing for reading the information of a given date
    '''

    results=db_helper_postgre.retrieve_date("2024-08-15")
    assert len(results)==1 #Just one element for this date
    assert results[0]["amount"]==10
    assert ( "Bought potatoes" in results[0]["notes"])==True 



#%% READ TESTING
def test_custom_query():
    '''
        1. Unitary testing for reading a custom query. Will retrieve the expenses with amounts >900
        2. Unitary testing for reading a custom query. Will retrieve the expesnes with amount >200 and category =Food
    '''
    
    #******** 1. Unitary testing
    where_dict={
        "amount":"900"
    }

    operator_dict={
        "amount":">"
    }

    results=db_helper_postgre.retrieve_custom_query(where_dict,operator_dict)
    assert results[0]["category"]=="Rent"
    assert results[0]["amount"]==1200

    #******** 2. Unitary testing
    where_dict={
        "amount":"200",
        "category":"Food"
    }

    operator_dict={
        "amount":">",
        "category":"="
    }

    results=db_helper_postgre.retrieve_custom_query(where_dict,operator_dict)
    assert len(results)==6


#%% UPDATE AND DELETE TESTING
def test_update():
    '''
        Unitary testing for updating records. Update a fictional record created for 2025-07-12   
    '''
    mapping_dict={
        "notes":"This is an update"
    }

    where_dict={
        "expense_date":"2025-07-12"
    }

    operator_dict={
        "expense_date":"="
    }

    _=db_helper_postgre.update_record(mapping_dict,where_dict,operator_dict)
    results=db_helper_postgre.retrieve_date("2025-07-12")
    assert results[0]["notes"]=="This is an update"

def test_delete():
    '''
        Unitary testing for deleting records. Will delete the fictional record created for 2025-07-12
    '''
    where_dict={
        "expense_date":"2025-07-12"
    }

    operator_dict={
        "expense_date":"="
    }
    _=db_helper_postgre.delete_record(where_dict,operator_dict)
    results=db_helper_postgre.retrieve_date("2025-07-12")
    assert len(results)==0

#%% OPERATORS AND COLUMNS TESTING
def test_where_operators_validation():
    '''  
        1. Unitary testing for Column names
        2. Unitary testing for operators
    '''

    #******* 1. Unitary testing
    where_dict={
        "date":"2024-08-12"
    }

    operator_dict={
        "expense_date":">"
    }

    with pytest.raises(ValueError):
        db_helper_postgre.validate_where_clause(where_dict,operator_dict)

    #******* 2. Unitary testing
    where_dict={
        "expense_date":"2024-08-12",
        "amount":100,
        "category":"Food",
        "notes":"Whatever"
    }

    operator_dict={
        "expense_date":">",
        "amount":"=",
        "category":"!=",
        "notes":"@"
    }
    with pytest.raises(ValueError):
        db_helper_postgre.validate_where_clause(where_dict,operator_dict)
