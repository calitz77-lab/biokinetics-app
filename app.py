import datetime
import sqlite3
import pandas as pd
import streamlit as st

# Initialize Database Architecture
def init_db():
    conn = sqlite3.connect("biokinetics_practice.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT, condition TEXT, medical_aid TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS appointments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client TEXT, service TEXT, status TEXT, amount REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS expenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount REAL, description TEXT)""")
    conn.commit()
    return conn

conn = init_db()

# Page Configuration
st.set_page_config(page_title="Christopher Calitz Biokinetics", page_icon="💪", layout="wide")

# Sidebar Navigation
st.sidebar.title("🩺 Christopher Calitz Biokinetics")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["📊 Executive Dashboard", "📅 Appointments", "👥 Client Database", "💰 Billing & Invoices", "🏋️ Program Builder"])

# Dashboard Module
if menu == "📊 Executive Dashboard":
    st.title("Executive Dashboard")
    
    appts = pd.read_sql("SELECT * FROM appointments WHERE status='Paid'", conn)
    expenses = pd.read_sql("SELECT * FROM expenses", conn)
    
    total_income = appts["amount"].sum() if not appts.empty else 0.0
    total_expenses = expenses["amount"].sum() if not expenses.empty else 0.0
    net_profit = total_income - total_expenses
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Target (R12,000)", f"R {total_income:,.2f}", f"{(total_income/12000)*100:.1f}%")
    col2.metric("Total Income", f"R {total_income:,.2f}")
    col3.metric("Practice Expenses", f"R {total_expenses:,.2f}")
    col4.metric("Net Profit", f"R {net_profit:,.2f}")

# Appointments Module
elif menu == "📅 Appointments":
    st.title("Appointments & WhatsApp Reminders")
    
    with st.form("book_appt"):
        col1, col2 = st.columns(2)
        client_name = col1.text_input("Client Name")
        phone = col1.text_input("Phone Number (e.g., 0821234567)")
        service = col1.selectbox("Service", ["Initial Assessment", "Follow-up", "Rehab Session"])
        
        appt_date = col2.date_input("Date")
        appt_time = col2.time_input("Time")
        amount = col2.number_input("Fee (ZAR)", value=750.0)
        
        if st.form_submit_button("Book Session"):
            full_date = f"{appt_date} {appt_time}"
            conn.execute("INSERT INTO appointments (date, client, service, status, amount) VALUES (?, ?, ?, ?, ?)", 
                         (full_date, client_name, service, "Booked", amount))
            conn.commit()
            st.success("Session Booked!")
            
            clean_phone = phone.lstrip("0")
            wa_link = f"https://wa.me/27{clean_phone}?text=Hi%20{client_name},%20reminder%20for%20your%20session%20with%20Christopher%20Calitz%20Biokinetics%20on%20{appt_date}%20at%20{appt_time}."
            st.markdown(f"**[📱 Click to Send WhatsApp Reminder]({wa_link})**")
            
    st.subheader("Upcoming Schedule")
    st.dataframe(pd.read_sql("SELECT * FROM appointments", conn), use_container_width=True)

# Client Database Module
elif menu == "👥 Client Database":
    st.title("Client Management")
    with st.form("new_client"):
        name = st.text_input("Full Name")
        phone = st.text_input("Contact Number")
        email = st.text_input("Email")
        condition = st.text_input("Condition/Injury")
        medical_aid = st.selectbox("Medical Aid", ["Private/Cash", "Discovery Health", "Momentum Health", "Bonitas", "Medihelp"])
        
        if st.form_submit_button("Save Client"):
            conn.execute("INSERT INTO clients (name, phone, email, condition, medical_aid) VALUES (?, ?, ?, ?, ?)", 
                         (name, phone, email, condition, medical_aid))
            conn.commit()
            st.success("Client added.")
            
    st.dataframe(pd.read_sql("SELECT * FROM clients", conn), use_container_width=True)

# Program Builder Module
elif menu == "🏋️ Program Builder":
    st.title("Bilingual Program Builder")
    lang = st.radio("Language", ["English", "Afrikaans"])
    
    if lang == "Afrikaans":
        st.subheader("Krag en Stabiliteit Oefeninge")
        st.write("1. Skons / Squats (3 x 10)\n2. Enkelbeen Balans (3 x 30s)\n3. Skyfskiet Stabilisasie")
    else:
        st.subheader("Strength and Stability")
        st.write("1. Squats (3 x 10)\n2. Single-Leg Balance (3 x 30s)\n3. Target Shooting Stabilization")
