# Attendance Check-In System

## 📌 Overview
This is a **QR Code-based Attendance System** built using **Streamlit** and **SQLite**. The system ensures that each QR code is **one-time use only**, preventing multiple check-ins using the same QR code.

## 🚀 Features
- **Admin QR Generation**: Each QR code is uniquely generated by the admin.
- **Unique QR Code Usage**: Each QR code is **valid for only one check-in**.
- **Prevent Cheating**: Students **cannot change emails** to check in multiple times.
- **Secure Storage**: Attendance records are stored in an **SQLite database**.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python (FastAPI in future updates)
- **Database:** SQLite
- **QR Code Generation:** qrcode library
- **Security:** Base64 Encoding & Unique Constraints

## 📷 Workflow
1️⃣ **Admin Generates QR Code** → A unique QR is generated with `scan_date` and `scan_time` encoded.
2️⃣ **Student Scans QR Code** → Redirected to the check-in page.
3️⃣ **Student Submits Check-In** → System verifies and stores attendance.
4️⃣ **Duplicate Check Prevention** → The same QR cannot be reused.

## 🔑 Database Schema
```sql
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_email TEXT,
    scan_date DATE,
    scan_time TIME,
    checkin_date DATE,
    checkin_time TIME,
    UNIQUE(scan_date, scan_time)
);
```

## 🏗️ Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/GRIITTYY/anti-cheat-checkin-system.git
cd anti-cheat-checkin-system
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

**OR** install them manually:

```bash
pip install streamlit pyyaml bcrypt qrcode pandas streamlit-option-menu pytz
```

### 3️⃣ Run the Streamlit App
```bash
streamlit run app.py
```

## 📖 Usage
### **Admin Panel**
- Generate QR codes for students.
- Each QR is **single-use** and prevents duplicate check-ins."

### **Student Check-In**
- Scan the QR code.
- Enter their registered email (doesn’t affect duplication check).
- Click **Check-in**.

## ❗ Anti-Cheat Measures
✔️ **Each QR is one-time use only.**  
✔️ **Email cannot be changed to bypass restrictions.**  
✔️ **Duplicate scan_date and scan_time entries are blocked.**  
✔️ **New QR must be generated for each check-in session.**  

## 🎯 Future Improvements
- ✅ **FastAPI backend** for improved performance.
- ✅ **MongoDB for scalable storage.**
- ✅ **Admin dashboard with user analytics.**

## 📜 License
This project is licensed under the MIT License. Feel free to use and improve it!

---
🚀 **Built with Python & Streamlit** | 👨‍💻 Maintained by [Samuel Momoh](https://github.com/GRIITTYY/)

