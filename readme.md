# 💸 Expense Tracker — Full-Stack SQL App (PostgreSQL + FastAPI + Streamlit)

Author: Sebastian Torres
Linkedin: https://www.linkedin.com/in/sebastian-torres-franco-3b3000115/
# ---

This project delivers a **complete end-to-end solution** for managing personal expense records using a cloud-hosted PostgreSQL database, a robust FastAPI backend, and a friendly Streamlit frontend.

The app allows users to perform flexible SQL operations through a web interface, including:
- Creating and updating expense records
- Running custom filters using SQL-like conditions
- Visualizing analytics across date ranges

---

##  Live Demo

> 🎯 [Try the live app](https://sql-crud-app-pythonpostgre-zxq6hzkbpyl25uyygefonx.streamlit.app/)  
> 🛠️ Backend powered by [FastAPI](https://sql-crud-app-pythonpostgre-production.up.railway.app/docs)  
> ☁️ Hosted via [Railway](https://railway.app)

---

## 📌 Project Highlights

✅ **ETL-Ready Backend:**  
- A PostgreSQL database hosted on Railway  
- Secure API access using environment variables and parameterized queries
- Full CRUD logic with validation and logging

✅ **FastAPI-Powered API:**  
- RESTful routes for Create, Read, Update, Delete, and Analytics  
- Paydantic validation for input format to minimize errors.
- Rigurous log elaboration based on the user actions
- Unitary testing of the API's functionalities using pytest
- Custom query handling with flexible WHERE + operator mappings  
- Deployed and documented at `/docs` with live Swagger UI

✅ **Streamlit Frontend:**  
- Intuitive UI for interacting with the backend  
- Form-based record creation, editing, deletion  
- Real-time analytics with Plotly visualizations

✅ **Cloud Native Deployment:**  
- Entire stack (API + DB + frontend) deployed on Railway and Streamlit Cloud  
- Secure handling of credentials using `st.secrets` and environment variables

---

## 📸 Screenshots

### 🧾 CRUD Operations  
<img src="assets/crud_example.png" width="600"/>

### 📊 Analytics Dashboard  
<img src="assets/analytics_dashboard.png" width="600"/>

---

## 🧱 Tech Stack

| Layer        | Tech                     |
|--------------|--------------------------|
| Frontend     | Streamlit                |
| Backend      | FastAPI                  |
| Database     | PostgreSQL (Railway)     |
| Data Viz     | Plotly, Pandas, Matplotlib |
| Hosting      | Railway + Streamlit Cloud |

---

## 🧰 Project Structure

project/
├── backend/
│ ├── db_helper_postgre.py # PostgreSQL logic + validations
│ └── server.py # FastAPI app with all routes
├── frontend/
│ └── streamlit_app.py # Streamlit UI logic
├── .streamlit/
│ └── secrets.toml # API_URL and secret management
├── requirements.txt # All dependencies
└── README.md 

## ⚙️ Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sql-crud-app-python_postgre.git
cd sql-crud-app-python_postgre
```

2. **Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Configure environment variables**
For FastAPI:
# .env file for backend
DATABASE_URL=postgresql://username:password@host:port/dbname

For streamlit:
.streamlit/secrets.toml
API_URL = "https://sql-crud-app-python-production.up.railway.app"

5. **Run the APP**
BACKEND:
```bash
uvicorn backend.server:server --reload
```
Frontend:
```bash
streamlit run frontend/streamlit_app.py
```







