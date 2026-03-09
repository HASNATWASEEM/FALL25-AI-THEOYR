# 📦 IPS Inventory & POS Management System

A robust, real-world **Inventory Management and Point of Sale (POS)** application built using Python (Flask). This system is designed for grocery stores to track stock, manage sales, and monitor financial health with automated PDF receipt generation.



## 🚀 Key Features

- **🔐 Secure Authentication:** Role-based access control (RBAC). 
  - *Managers:* Full access (Add/Update stock, view logs, profit analysis).
  - *Staff:* Can only search products and process sales.
- **🔍 Barcode Integration:** Integrated barcode scanning feature for rapid product lookups and billing.
- **📉 Real-time Profit/Loss Analysis:** - Automatic calculation of daily profits.
  - **Financial Warning System:** Alerts managers if an item's sale price is set below its cost price to prevent losses.
- **🧾 Automated PDF Receipts:** Generates professional, downloadable PDF slips for customers instantly using `ReportLab`.
- **📜 Activity Logging:** Every action (Login, Logout, Stock Update) is tracked for audit purposes.
- **📱 Responsive UI:** Built with Bootstrap 5, making it accessible on both desktops and tablets.

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla)
- **Database:** JSON (Flat-file storage for lightweight portability)
- **PDF Generation:** ReportLab
- **Security:** Werkzeug (Password Hashing)



## 📸 Screenshots

*(Tip: Add your project screenshots here to make it more visual)*

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/ips-inventory-system.git](https://github.com/yourusername/ips-inventory-system.git)
   cd ips-inventory-system
Install Dependencies:Bashpip install flask flask-login reportlab werkzeug
Run the Application:Bashpython app.py
Access in Browser: Go to http://127.0.0.1:5000📊 Logic Spotlight: Financial GuardrailThe system includes a unique logic to protect business margins:$$PotentialLoss = (CostPrice - SalePrice) \times Quantity$$If $SalePrice < CostPrice$, the system flags the item in the "Potential Loss" dashboard to alert the manager.