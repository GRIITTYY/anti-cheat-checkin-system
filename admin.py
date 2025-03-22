import streamlit as st
import yaml
import bcrypt
import time
import qrcode
from datetime import datetime
from io import BytesIO
import base64
import sqlite3
import pandas as pd


def admin_section():
    # --- FUNCTIONS ---

    # Load admin credentials from Streamlit Secrets
    def load_admin_credentials():
        try:
            return st.secrets["admin"]
        except KeyError:
            return {}

    # Load normal users from YAML file
    def load_users():
        try:
            with open("user_config.yaml", "r") as file:
                return yaml.safe_load(file) or {"credentials": {"usernames": {}}}
        except FileNotFoundError:
            return {"credentials": {"usernames": {}}}

    # Hash password
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    # Verify password against hashed version
    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    # Verify admin login
    def verify_admin(username, password):
        admin_creds = load_admin_credentials()
        return username == admin_creds.get("username") and password == admin_creds.get("password")

    # Verify normal user login
    def verify_user(username, password):
        users = load_users()["credentials"]["usernames"]
        if username in users:
            return verify_password(password, users[username]["password"])
        return False

    # Load or initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.session_state.page = "login"

    # --- LOGIN SCREEN ---
    if st.session_state.page == "login":
        st.title("Login Portal")
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username")
            if username:
                st.session_state['username'] = username
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
        
        if login_button:
            if verify_admin(username, password):
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.page = "user_management"
                st.success("✅ Admin login successful! Redirecting...")
                time.sleep(1)
                st.rerun()
            elif verify_user(username, password):
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.session_state.page = "welcome"
                st.success("✅ User login successful! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    # --- USER MANAGEMENT DASHBOARD (ADMIN ONLY) ---
    elif st.session_state.page == "user_management":
        
        st.title("User Management Dashboard")
        config_data = load_users()
        usernames = list(config_data["credentials"]["usernames"].keys())
        
        # Add User
        with st.expander("➕ Add User", expanded=False):
            with st.form("add_user_form", clear_on_submit=True):
                username = st.text_input("Username")
                email = st.text_input("Email")
                full_name = st.text_input("Full Name")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Add User")
            
            if submit_button:
                if username and email and full_name and password:
                    
                    config_data["credentials"]["usernames"][username] = {
                        "email": email,
                        "name": full_name,
                        "password": hash_password(password)
                    }
                    with open("user_config.yaml", "w") as file:
                        yaml.safe_dump(config_data, file)
                    st.success(f"User '{username}' added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Please fill in all fields.")
        
        # Remove User
        with st.expander("🗑️ Remove User", expanded=False):
            removed_users = []
            if usernames:
                with st.form("remove_user_form", clear_on_submit=True):
                    selected_users = st.multiselect("Select user(s) to remove", usernames, placeholder="Choose user(s)")
                    remove_button = st.form_submit_button("Remove Selected Users")
                
                if remove_button and selected_users:
                    for user in selected_users:
                        del config_data["credentials"]["usernames"][user]
                        removed_users.append(username)
                    with open("user_config.yaml", "w") as file:
                        yaml.safe_dump(config_data, file)
                    for username in removed_users:
                        st.success(f"✅ User '{username}' removed successfully!")
                    time.sleep(2)
                    st.rerun()
            else:
                st.warning("⚠️ No users available to remove.")
        
        # Update User
        with st.expander("✏️ Update User Credentials", expanded=False):
            if usernames:
                with st.form("update_user_form", clear_on_submit=True):
                    selected_user = st.selectbox("Select user to update", usernames)
                    new_email = st.text_input("New Email (leave blank to keep current)")
                    new_name = st.text_input("New Full Name (leave blank to keep current)")
                    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                    update_button = st.form_submit_button("Update User")
                
                if update_button:
                    if selected_user in config_data["credentials"]["usernames"]:
                        if new_email:
                            config_data["credentials"]["usernames"][selected_user]["email"] = new_email
                        if new_name:
                            config_data["credentials"]["usernames"][selected_user]["name"] = new_name
                        if new_password:
                            config_data["credentials"]["usernames"][selected_user]["password"] = hash_password(new_password)
                        with open("user_config.yaml", "w") as file:
                            yaml.safe_dump(config_data, file)
                        st.success(f'User "{selected_user}" updated successfully!')
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.warning("User not found.")
            else:
                st.warning("⚠️ No users available to update.")
            
        if st.button("Logout 🚪"):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.page = "login"
            st.rerun()


    # --- WELCOME SCREEN (NORMAL USERS) ---
    elif st.session_state.page == "welcome":
        st.title("Welcome to the Platform!")
        st.write("Please generate a QR Code below for each user.")

        # Generate QR Code
        if st.button("Generate QR Code"):
            username = st.session_state.get("username", "unknown_user")
            now = datetime.now()
            date_str = now.strftime("%d%m%Y")
            time_str = now.strftime("%H%M%S")

            # Data to encode
            raw_data = f"{username}|{date_str}|{time_str}"

            # Encode data using Base64
            encoded_data = base64.urlsafe_b64encode(raw_data.encode()).decode()
            checkin_url = f"http://checkin-system.streamlit.app/?data={encoded_data}"
            # checkin_url = f"http://localhost:8501/?data={encoded_data}" #


            # Create QR Code with encoded data
            qr = qrcode.make(checkin_url)
            qr_bytes = BytesIO()
            qr.save(qr_bytes, format="PNG")
            qr_bytes.seek(0)  # Move to start so Streamlit can read it

            # Display QR Code
            st.image(qr_bytes, caption="Scan the QR Code above to Check-In")

            # Optionally, show the actual URL (for debugging)
            st.write(f"### Check-In URL:")
            st.markdown(f"[{checkin_url}]({checkin_url})")


                    # Connect to SQLite database
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()

            # Create attendance table if not exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_email TEXT,
                scan_date DATE,
                scan_time TIME,
                student_email TEXT,
                checkin_date DATE,
                checkin_time TIME,
                UNIQUE(scan_date, scan_time))
            """)
            conn.commit()

            # Streamlit UI
            st.header("View attendance data.")

            # Fetch data from the selected table
            query = f"SELECT * FROM attendance"
            df = pd.read_sql(query, conn)

            # Display the data
            st.write(f"### Data from `attendance` table")
            st.dataframe(df)  # Streamlit's interactive table


            # Close the database connection
            conn.close()

        if st.button("Logout 🚪"):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.page = "login"
            st.rerun()