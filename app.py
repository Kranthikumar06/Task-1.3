import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib


load_dotenv(dotenv_path='.env')






# Database connection function using .env
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('AIVEN_MYSQL_PASS'),
        database=os.getenv('data'),
        port=int(os.getenv('port'))
    )
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False, "Username already exists."
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hash_password(password)))
    conn.commit()
    cur.close()
    conn.close()
    return True, "Registration successful."

def login_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                (username, hash_password(password)))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def login_admin(username, password):
    # Hardcoded admin credentials (change as needed)
    admin_user = "admin"
    admin_pass = "admin123"
    return username == admin_user and password == admin_pass

def create_complaint(name, email, category, description):
    conn = get_db_connection()
    cur = conn.cursor()
    sql = ("INSERT INTO complaints (name, email, category, description, status, created_at) "
           "VALUES (%s, %s, %s, %s, 'Open', %s)")
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(sql, (name, email, category, description, now))
    conn.commit()
    complaint_id = cur.lastrowid
    cur.close()
    conn.close()
    return complaint_id

def get_complaint_by_id(complaint_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM complaints WHERE id = %s', (complaint_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


st.title('Online Complaint Management System')


if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Sidebar role selection (User/Admin) before login
if not st.session_state['user_logged_in'] and not st.session_state['admin_logged_in']:
    main_menu = st.sidebar.selectbox('Select Role', ['User', 'Admin'])
else:
    if st.session_state.get('user_logged_in'):
        main_menu = 'User'
    else:
        main_menu = 'Admin'

if main_menu == 'User':
    if not st.session_state['user_logged_in']:
        user_menu = st.sidebar.selectbox('User Menu', ['Login', 'Register'])
        if user_menu == 'Register':
            st.subheader('User Registration')
            with st.form('register_form'):
                username = st.text_input('Username')
                email = st.text_input('Email')
                password = st.text_input('Password', type='password')
                reg_submit = st.form_submit_button('Register')
            if reg_submit:
                if not username or not email or not password:
                    st.error('All fields required.')
                elif '@' not in email or '.' not in email:
                    st.error('Invalid email address.')
                else:
                    success, msg = register_user(username, email, password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
        else:
            st.subheader('User Login')
            with st.form('login_form'):
                username = st.text_input('Username')
                password = st.text_input('Password', type='password')
                login_submit = st.form_submit_button('Login')
            if login_submit:
                user = login_user(username, password)
                if user:
                    st.session_state['user_logged_in'] = True
                    st.session_state['current_user'] = user
                    st.success('Login successful!')
                    st.rerun()
                else:
                    st.error('Invalid credentials.')
    else:
        if st.sidebar.button('Logout'):
            st.session_state['user_logged_in'] = False
            st.session_state['current_user'] = None
            st.rerun()
        if 'user_menu' not in st.session_state:
            st.session_state['user_menu'] = 'Submit Complaint'
        menu = st.sidebar.selectbox('User Menu', ['Submit Complaint', 'Search Complaint'], index=['Submit Complaint', 'Search Complaint'].index(st.session_state.get('user_menu', 'Submit Complaint')))
        st.session_state['user_menu'] = menu
        if menu == 'Submit Complaint':
            st.header('Submit a Complaint')
            with st.form('complaint_form'):
                name = st.text_input('Name', value=st.session_state['current_user']['username'])
                email = st.text_input('Email', value=st.session_state['current_user']['email'])
                category = st.selectbox('Category', [
                    'Hostel',
                    'Mess',
                    'Academics',
                    'Library',
                    'Sports',
                    'Transport',
                    'Infrastructure',
                    'Examination',
                    'Placement',
                    'Other',
                ])
                description = st.text_area('Description')
                submitted = st.form_submit_button('Submit')
            if submitted:
                if not name or not email or not description:
                    st.error('Please fill all required fields.')
                elif '@' not in email or '.' not in email:
                    st.error('Please enter a valid email address.')
                else:
                    complaint_id = create_complaint(name, email, category, description)
                    st.success(f'Complaint submitted! Your Complaint ID is {complaint_id}.')
        elif menu == 'Search Complaint':
            st.header('Search Complaint by ID')
            search_id = st.text_input('Enter Complaint ID')
            if st.button('Search'):
                if not search_id.isdigit():
                    st.error('Please enter a valid numeric Complaint ID.')
                else:
                    row = get_complaint_by_id(int(search_id))
                    if row:
                        with st.expander('Complaint Details'):
                            st.write(f"**ID:** {row['id']}")
                            st.write(f"**Name:** {row['name']}")
                            st.write(f"**Email:** {row['email']}")
                            st.write(f"**Category:** {row['category']}")
                            st.write(f"**Description:** {row['description']}")
                            st.write(f"**Status:** {row['status']}")
                            st.write(f"**Created At:** {row['created_at']}")



# (Removed leftover st.radio for role selection)

if main_menu == 'Admin':
    if not st.session_state['admin_logged_in']:
        st.subheader('Admin Login')
        with st.form('admin_login_form'):
            username = st.text_input('Admin Username')
            password = st.text_input('Admin Password', type='password')
            admin_login_submit = st.form_submit_button('Login')
        if admin_login_submit:
            if login_admin(username, password):
                st.session_state['admin_logged_in'] = True
                st.success('Admin login successful!')
                st.rerun()
            else:
                st.error('Invalid admin credentials.')
    elif st.session_state['admin_logged_in']:
        if st.sidebar.button('Logout'):
            st.session_state['admin_logged_in'] = False
            st.rerun()
        if 'admin_menu' not in st.session_state:
            st.session_state['admin_menu'] = 'View All Complaints'
        menu = st.sidebar.selectbox('Admin Menu', ['View All Complaints', 'Search Complaint by ID'], index=['View All Complaints', 'Search Complaint by ID'].index(st.session_state.get('admin_menu', 'View All Complaints')))
        st.session_state['admin_menu'] = menu
        if menu == 'View All Complaints':
            st.header('All Complaints')
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM complaints ORDER BY created_at DESC')
            complaints = cur.fetchall()
            cur.close()
            conn.close()
            for row in complaints:
                with st.expander(f"Complaint ID: {row['id']} | Status: {row['status']}"):
                    st.write(f"**Name:** {row['name']}")
                    st.write(f"**Email:** {row['email']}")
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Created At:** {row['created_at']}")
                    new_status = st.selectbox('Update Status', ['Open', 'In Progress', 'Closed'], index=['Open', 'In Progress', 'Closed'].index(row['status']), key=f'status_{row['id']}')
                    if st.button('Update Status', key=f'btn_{row['id']}'):
                        conn2 = get_db_connection()
                        cur2 = conn2.cursor()
                        cur2.execute('UPDATE complaints SET status = %s WHERE id = %s', (new_status, row['id']))
                        conn2.commit()
                        cur2.close()
                        conn2.close()
                        st.success('Status updated! Please refresh to see changes.')
        elif menu == 'Search Complaint by ID':
            st.header('Search Complaint by ID')
            search_id = st.text_input('Enter Complaint ID')
            if st.button('Search'):
                if not search_id.isdigit():
                    st.error('Please enter a valid numeric Complaint ID.')
                else:
                    conn = get_db_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute('SELECT * FROM complaints WHERE id = %s', (int(search_id),))
                    row = cur.fetchone()
                    cur.close()
                    conn.close()
                    if row:
                        with st.expander('Complaint Details'):
                            st.write(f"**ID:** {row['id']}")
                            st.write(f"**Name:** {row['name']}")
                            st.write(f"**Email:** {row['email']}")
                            st.write(f"**Category:** {row['category']}")
                            st.write(f"**Description:** {row['description']}")
                            st.write(f"**Status:** {row['status']}")
                            st.write(f"**Created At:** {row['created_at']}")
                            new_status = st.selectbox('Update Status', ['Open', 'In Progress', 'Closed'], index=['Open', 'In Progress', 'Closed'].index(row['status']), key=f'status_search_{row['id']}')
                            if st.button('Update Status', key=f'btn_search_{row['id']}'):
                                conn2 = get_db_connection()
                                cur2 = conn2.cursor()
                                cur2.execute('UPDATE complaints SET status = %s WHERE id = %s', (new_status, row['id']))
                                conn2.commit()
                                cur2.close()
                                conn2.close()
                                st.success('Status updated! Please refresh to see changes.')
                    else:
                        st.warning('Complaint not found.')
