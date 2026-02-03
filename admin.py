import streamlit as st
import mysql.connector
from connection import MYSQL_CONFIG

# Database helper functions
def get_db_connection():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    return conn

def get_all_complaints():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM complaints ORDER BY created_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def update_complaint_status(complaint_id, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE complaints SET status = %s WHERE id = %s', (status, complaint_id))
    conn.commit()
    cur.close()
    conn.close()

def get_complaint_by_id(complaint_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM complaints WHERE id = %s', (complaint_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

# Streamlit UI
st.title('Admin Dashboard')

menu = ['View All Complaints', 'Search Complaint by ID']
choice = st.sidebar.selectbox('Admin Menu', menu)

if choice == 'View All Complaints':
    st.header('All Complaints')
    complaints = get_all_complaints()
    for row in complaints:
        with st.expander(f"Complaint ID: {row['id']} | Status: {row['status']}"):
            st.write(f"**Name:** {row['name']}")
            st.write(f"**Email:** {row['email']}")
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Description:** {row['description']}")
            st.write(f"**Created At:** {row['created_at']}")
            new_status = st.selectbox('Update Status', ['Open', 'In Progress', 'Closed'], index=['Open', 'In Progress', 'Closed'].index(row['status']), key=f'status_{row['id']}')
            if st.button('Update Status', key=f'btn_{row['id']}'):
                update_complaint_status(row['id'], new_status)
                st.success('Status updated! Please refresh to see changes.')

elif choice == 'Search Complaint by ID':
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
                    new_status = st.selectbox('Update Status', ['Open', 'In Progress', 'Closed'], index=['Open', 'In Progress', 'Closed'].index(row['status']), key=f'status_search_{row['id']}')
                    if st.button('Update Status', key=f'btn_search_{row['id']}'):
                        update_complaint_status(row['id'], new_status)
                        st.success('Status updated! Please refresh to see changes.')
            else:
                st.warning('Complaint not found.')
