# 📦 Inventory Control System - DBMS Mini Project

A robust, database-driven Inventory Management System built as a 3rd-year B.Tech Database Management System (DBMS) mini-project. This application features a modern web interface, real-time stock tracking, and automated database triggers to ensure strict relational integrity during stock movements.

## ✨ Key Features

* **Multi-User Secure Authentication:** Role-based access control allowing specific administrators to log in securely.
* **Real-Time Dashboard Insights:** Instant calculation of total unique products, overall inventory valuation, and automated low-stock alerts.
* **Automated Database Triggers:** The core DBMS feature. Stock levels (`quantity_in_stock`) in the Products table are automatically updated via SQL `AFTER INSERT` triggers whenever a new IN/OUT transaction is recorded, eliminating the need for manual stock calculation.
* **Full CRUD Operations:** Intuitive UI to Add, Edit, and Delete products. Deleting a product automatically cascades to remove its transaction history, preventing foreign key constraint violations.
* **Alphanumeric Transaction Tracking:** Auto-generates unique, professional transaction IDs (e.g., `TXN-A8F3K9M2L1`) for every stock movement.

## 🛠️ Technology Stack

* **Frontend Framework:** Python (Streamlit)
* **Database Engine:** SQLite3 (Serverless, local relational database)
* **Data Processing:** Pandas (For SQL query structuring and UI rendering)

## 🗄️ Database Schema Design

The system relies on a strictly relational schema built with the following core entities:

1. **`Products` Table:**
   * `product_id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Formatted as `INV#001` on the frontend.
   * `product_name` (TEXT)
   * `unit_price` (REAL)
   * `quantity_in_stock` (INTEGER)
   * `reorder_level` (INTEGER)

2. **`Transactions` Table:**
   * `transaction_id` (TEXT PRIMARY KEY) - Alphanumeric hash.
   * `product_id` (INTEGER) - Foreign Key referencing `Products(product_id)`.
   * `transaction_type` (TEXT) - 'IN' or 'OUT'.
   * `quantity` (INTEGER)
   * `transaction_date` (TIMESTAMP)

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher installed on your system.
* Git installed on your system.

### Step-by-Step Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
   cd YOUR_REPOSITORY_NAME
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python -m streamlit run app.py
   ```
   *Note: If you encounter a PATH error on Windows, use the command above rather than just `streamlit run app.py`.*

## 🔐 Default Login Credentials

Upon running the application, use one of the following administrator accounts to access the dashboard:

* **User 1:** 
  * Username: `abhay`
  * Password: `abhay@001`
* **User 2:**
  * Username: `yash`
  * Password: `yash@061`

## 📂 Project Structure

```text
├── app.py                  # Main Streamlit application and SQL logic
├── requirements.txt        # Python package dependencies
├── .gitignore              # Ignored files (including the local database)
└── README.md               # Project documentation
```
*Note: The `inventory_system.db` file is automatically generated locally on the first run and is intentionally excluded from the repository via `.gitignore`.*

## 👨‍💻 Project Creators

* **Abhay Kumar**
* **Yash Pandey**