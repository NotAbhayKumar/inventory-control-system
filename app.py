import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
import random
import string

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Inventory System", page_icon="📦", layout="wide")

# --- DATABASE SETUP (SQLite3) ---
def get_db_connection():
    conn = sqlite3.connect('inventory_system.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Products table (product_id stays integer for DB logic, formatted on frontend)
    c.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity_in_stock INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 10
        )
    ''')
    
    # Transactions table (transaction_id changed to TEXT for alphanumeric IDs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id TEXT PRIMARY KEY,
            product_id INTEGER,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')
    
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS after_transaction_insert_in
        AFTER INSERT ON Transactions
        WHEN NEW.transaction_type = 'IN'
        BEGIN
            UPDATE Products 
            SET quantity_in_stock = quantity_in_stock + NEW.quantity 
            WHERE product_id = NEW.product_id;
        END;
    ''')

    c.execute('''
        CREATE TRIGGER IF NOT EXISTS after_transaction_insert_out
        AFTER INSERT ON Transactions
        WHEN NEW.transaction_type = 'OUT'
        BEGIN
            UPDATE Products 
            SET quantity_in_stock = quantity_in_stock - NEW.quantity 
            WHERE product_id = NEW.product_id;
        END;
    ''')
    
    conn.commit()
    return conn

# Helper function to generate alphanumeric transaction IDs
def generate_txn_id():
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=8))
    return f"TXN-{random_str}"

init_db()
conn = get_db_connection()

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""

# --- VALID USER CREDENTIALS ---
VALID_USERS = {
    "abhay": "abhay@001",
    "yash": "yash@061"
}

# --- PAGE 1: LOGIN UI ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>📦 Inventory</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Secure System Login</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username in VALID_USERS and VALID_USERS[username] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
else:
    # --- PAGE 2: MAIN DASHBOARD UI ---
    st.sidebar.title("📦 Inventory")
    st.sidebar.success(f"Logged in as: **{st.session_state['current_user'].capitalize()}**")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navigation Menu", ["Dashboard Insights", "Manage Products", "Stock In/Out", "Transaction History"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Project By:")
    st.sidebar.markdown("- **Abhay Kumar**\n- **Yash Pandey**")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = ""
        st.rerun()

    # --- MENU: DASHBOARD INSIGHTS ---
    if menu == "Dashboard Insights":
        st.title("Dashboard Insights")
        df_products = pd.read_sql_query("SELECT * FROM Products", conn)
        
        if not df_products.empty:
            col1, col2, col3 = st.columns(3)
            
            total_products = len(df_products)
            total_value = (df_products['quantity_in_stock'] * df_products['unit_price']).sum()
            low_stock = len(df_products[df_products['quantity_in_stock'] <= df_products['reorder_level']])
            
            col1.metric("Total Unique Products", total_products)
            col2.metric("Total Inventory Value", f"₹{total_value:,.2f}")
            col3.metric("Low Stock Alerts", low_stock, delta_color="inverse")
            
            st.markdown("### Current Stock Levels")
            # Format product_id as INV#001 on the frontend display
            df_products['product_id'] = df_products['product_id'].apply(lambda x: f"INV#{x:03d}")
            st.dataframe(
                df_products[['product_id', 'product_name', 'quantity_in_stock', 'unit_price', 'reorder_level']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No products in inventory yet. Go to 'Manage Products' to add stock.")

    # --- MENU: MANAGE PRODUCTS ---
    elif menu == "Manage Products":
        st.title("Manage Products")
        
        # 1. ADD PRODUCT SECTION
        with st.expander("➕ Add New Product", expanded=False):
            with st.form("add_product_form"):
                p_name = st.text_input("Product Name")
                p_price = st.number_input("Unit Price (₹)", min_value=0.0, format="%.2f")
                p_reorder = st.number_input("Reorder Alert Level", min_value=0, value=10)
                submit_product = st.form_submit_button("Add to Database")
                
                if submit_product and p_name:
                    c = conn.cursor()
                    c.execute("INSERT INTO Products (product_name, unit_price, reorder_level) VALUES (?, ?, ?)", 
                              (p_name, p_price, p_reorder))
                    conn.commit()
                    st.success(f"Product '{p_name}' added successfully!")
                    time.sleep(1.5)
                    st.rerun()

        # 2. EDIT PRODUCT SECTION
        with st.expander("✏️ Edit Product", expanded=False):
            df_for_edit = pd.read_sql_query("SELECT * FROM Products", conn)
            
            if not df_for_edit.empty:
                # Create a professional dropdown label combining INV# and Name
                df_for_edit['display_label'] = df_for_edit.apply(lambda row: f"INV#{row['product_id']:03d} - {row['product_name']}", axis=1)
                product_dict_edit = dict(zip(df_for_edit.display_label, df_for_edit.product_id))
                
                edit_product_selection = st.selectbox("Select Product to Edit", options=list(product_dict_edit.keys()))
                
                # Fetch current values to pre-fill the form
                selected_p_id = product_dict_edit[edit_product_selection]
                current_data = df_for_edit[df_for_edit['product_id'] == selected_p_id].iloc[0]
                
                with st.form("edit_product_form"):
                    new_name = st.text_input("Product Name", value=current_data['product_name'])
                    new_price = st.number_input("Unit Price (₹)", min_value=0.0, value=float(current_data['unit_price']), format="%.2f")
                    new_reorder = st.number_input("Reorder Alert Level", min_value=0, value=int(current_data['reorder_level']))
                    submit_edit = st.form_submit_button("Update Product")
                    
                    if submit_edit:
                        c = conn.cursor()
                        c.execute("UPDATE Products SET product_name = ?, unit_price = ?, reorder_level = ? WHERE product_id = ?",
                                  (new_name, new_price, new_reorder, selected_p_id))
                        conn.commit()
                        st.success(f"Product updated successfully!")
                        time.sleep(1.5)
                        st.rerun()
            else:
                st.info("No products available to edit.")

        # 3. DELETE PRODUCT SECTION
        with st.expander("❌ Delete Product", expanded=False):
            df_for_delete = pd.read_sql_query("SELECT product_id, product_name FROM Products", conn)
            
            if not df_for_delete.empty:
                with st.form("delete_product_form"):
                    df_for_delete['display_label'] = df_for_delete.apply(lambda row: f"INV#{row['product_id']:03d} - {row['product_name']}", axis=1)
                    product_dict_del = dict(zip(df_for_delete.display_label, df_for_delete.product_id))
                    
                    del_product_selection = st.selectbox("Select Product to Delete", options=list(product_dict_del.keys()))
                    st.warning("Warning: Deleting a product will also delete its entire transaction history.")
                    submit_delete = st.form_submit_button("Delete Product")
                    
                    if submit_delete:
                        p_id_del = product_dict_del[del_product_selection]
                        c = conn.cursor()
                        c.execute("DELETE FROM Transactions WHERE product_id = ?", (p_id_del,))
                        c.execute("DELETE FROM Products WHERE product_id = ?", (p_id_del,))
                        conn.commit()
                        st.success("Product and its history have been deleted.")
                        time.sleep(1.5)
                        st.rerun()
            else:
                st.info("No products available to delete.")
        
        st.markdown("### Product Catalog")
        df_products_catalog = pd.read_sql_query("SELECT * FROM Products", conn)
        if not df_products_catalog.empty:
            df_products_catalog['product_id'] = df_products_catalog['product_id'].apply(lambda x: f"INV#{x:03d}")
            st.dataframe(df_products_catalog, use_container_width=True, hide_index=True)

    # --- MENU: STOCK IN / OUT ---
    elif menu == "Stock In/Out":
        st.title("Process Transactions")
        
        df_products = pd.read_sql_query("SELECT product_id, product_name FROM Products", conn)
        if df_products.empty:
            st.warning("Please add products first before processing transactions.")
        else:
            df_products['display_label'] = df_products.apply(lambda row: f"INV#{row['product_id']:03d} - {row['product_name']}", axis=1)
            product_dict = dict(zip(df_products.display_label, df_products.product_id))
            
            with st.form("transaction_form"):
                sel_product = st.selectbox("Select Product", options=list(product_dict.keys()))
                t_type = st.radio("Transaction Type", ["IN (Receive Shipment)", "OUT (Sell/Dispatch)"])
                t_qty = st.number_input("Quantity", min_value=1, step=1)
                submit_trans = st.form_submit_button("Process Transaction")
                
                if submit_trans:
                    p_id = product_dict[sel_product]
                    t_type_db = "IN" if "IN" in t_type else "OUT"
                    txn_id = generate_txn_id() # Generate the random alphanumeric ID
                    
                    c = conn.cursor()
                    c.execute("INSERT INTO Transactions (transaction_id, product_id, transaction_type, quantity) VALUES (?, ?, ?, ?)",
                              (txn_id, p_id, t_type_db, t_qty))
                    conn.commit()
                    
                    st.success(f"Transaction {txn_id} created: {t_qty} units {t_type_db} for {sel_product}!")
                    time.sleep(2)
                    st.rerun()

    # --- MENU: TRANSACTION HISTORY ---
    elif menu == "Transaction History":
        st.title("Transaction Log")
        
        query = '''
            SELECT t.transaction_id, p.product_id, p.product_name, t.transaction_type, t.quantity, t.transaction_date 
            FROM Transactions t
            JOIN Products p ON t.product_id = p.product_id
            ORDER BY t.transaction_date DESC
        '''
        df_trans = pd.read_sql_query(query, conn)
        
        if not df_trans.empty:
            # Format the product ID for display here too
            df_trans['product_id'] = df_trans['product_id'].apply(lambda x: f"INV#{x:03d}")
            st.dataframe(df_trans, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions recorded yet.")