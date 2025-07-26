#%% Import and app initialization

#Library imports
from fastapi import FastAPI,HTTPException
from datetime import date
from backend import db_helper_postgre 
from typing import List,Optional,Dict
import pydantic
from pydantic import BaseModel
import datetime
from datetime import date

#Initializing the app
server=FastAPI()

#%% Defining response base model

class expense_model(BaseModel): #This class will to retrieve a subset for fetch date queries
    amount:float
    category:str
    notes:Optional[str]=None

class expense_payload(BaseModel):
    expense_date:date
    entries:List[expense_model]

class expense_model_where_mapping(BaseModel): #This class contains a flexible type hint for all columns. This will help to manage custom select and where clauses
    expense_date:Optional[date]=None
    amount:Optional[float]=None
    category:Optional[str]=None
    notes:Optional[str]=None

class operator_model(BaseModel): #This class contains a flexible type hint for all operators. This will help to manage custom select and where clauses
    expense_date:Optional[str]=None
    amount:Optional[str]=None
    category:Optional[str]=None
    notes:Optional[str]=None

class expense_custom_query(BaseModel):
    where_info:expense_model_where_mapping
    operator_info:operator_model

class expense_set_mapping(BaseModel):
    set_info:expense_model_where_mapping
    where_info:expense_model_where_mapping
    operator_info:operator_model
 
class expense_date_range(BaseModel):
    start_date:date
    end_date:date

#%% Endpoint for retrieve date

@server.get("/expenses/fetch_date/{expense_date}",response_model=List[expense_model]) #This will return the subset defined in fetch_date_model
def get_expenses_by_date(expense_date:date):
    results=db_helper_postgre.retrieve_date(expense_date)
    if len(results)==0: 
        raise HTTPException(status_code=500,detail="Failed to retrieve data or date does not exist in database")
    return results
#%% Endpoint to create a record

@server.post("/expenses")
def create_expense(expense_info:expense_payload):
    for entry in expense_info.entries:
        db_helper_postgre.create_record(
            expense_date=expense_info.expense_date,
            amount=entry.amount,
            category=entry.category,
            notes=entry.notes
        ) 
#%% Endpoint to custom query
@server.post("/expenses/custom_query")
def custom_query(payload:expense_custom_query):
    #****** Form the where query
    where_dict=payload.where_info.model_dump()
    operator_dict=payload.operator_info.model_dump()
    results=db_helper_postgre.retrieve_custom_query(where_dict,operator_dict)
    if len(results)==0: 
        raise HTTPException(status_code=500,detail="No records match the where conditions")

    return results

#%% Endpoint to delete record
@server.delete("/expenses")
def server_delete(payload:expense_custom_query):
    where_dict=payload.where_info.model_dump()
    operator_dict=payload.operator_info.model_dump()
    num_records=db_helper_postgre.delete_record(where_dict,operator_dict)
    return {"action":"delete","status": "Success","records_deleted":num_records}
#%% Endpoint to update record
@server.put("/expenses")
def server_update(payload:expense_set_mapping):
    set_dict=payload.set_info.model_dump()
    where_dict=payload.where_info.model_dump()
    operator_dict=payload.operator_info.model_dump()
    num_records=db_helper_postgre.update_record(set_dict,where_dict,operator_dict)
    return {"action":"update","status": "Success","records_updated":num_records}

#%% Endpoint for analytics
@server.post("/analytics")
def server_analytics(payload:expense_date_range):
    start_date=payload.start_date
    end_date=payload.end_date
    total_expense,top_expense=db_helper_postgre.expense_summary(start_date,end_date)
    return {
        "summary_by_category": total_expense,
        "top_expenses": top_expense
    }