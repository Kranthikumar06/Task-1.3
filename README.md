# Online Complaint Management System

A simple web app to register and manage complaints using Streamlit and MySQL.

## Features
- Users can submit complaints (Name, Email, Category, Description)
- Auto-generated complaint ID
- Admin can view, update, and search complaints
- Complaint status: Open, In Progress, Closed
- Input validation

## Files
- `app.py`: User interface for complaint submission and search
- `admin.py`: Admin dashboard for managing complaints
- `schema.sql`: Database schema
- `README.md`: This file

## Setup
1. Install requirements:
   ```bash
   pip install streamlit mysql-connector-python
   ```
2. Create a MySQL database and table:
   - Create a database (e.g., `complaints_db`).
   - Run the SQL in `schema.sql` using your MySQL client:
     ```sql
     CREATE DATABASE complaints_db;
     USE complaints_db;
     -- Then run the contents of schema.sql
     ```
3. Configure MySQL connection:
   - Edit `mysql_config.py` with your MySQL credentials.
4. Run the user app:
   ```bash
   streamlit run app.py
   ```
5. Run the admin app:
   ```bash
   streamlit run admin.py
   ```

## Database
- Uses MySQL (`complaints_db`)
- Table: `complaints(id, name, email, category, description, status, created_at)`

## Notes
- For demo purposes, no authentication is implemented for admin.
- Extend as needed for production use.
