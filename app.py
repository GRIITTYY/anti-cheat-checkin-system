import streamlit as st
from io import BytesIO
from streamlit_option_menu import option_menu
from datetime import datetime
from urllib.parse import unquote
import json
import sqlite3
import pytz
import base64
import admin  # Import the admin file

# Set up sidebar navigation
with st.sidebar:
    page = option_menu(
        "Menu",
        ["MARK MY ATTENDANCE", "ADMIN LOGIN"],
        icons=["pencil-square", "lock"],
        menu_icon="justify",
        styles={
            "container": {"background-color": "#fafafa"},
            "nav-link": {"font-size": "17px", "text-align": "justify", "margin": "0px", "--hover-color": "#eee"}
        }
    )

import streamlit as st
import sqlite3
import base64
import pytz
from urllib.parse import unquote
from datetime import datetime

def mark_attendance():
    """Handles the attendance marking process."""
    query_params = st.query_params

    if "data" in query_params:
        data_param = query_params["data"]
        try:
            # Decode the URL parameter
            decoded_data_param = unquote(data_param)
            decoded_bytes = base64.urlsafe_b64decode(decoded_data_param)
            data_str = decoded_bytes.decode("utf-8")

            # Extract values
            username, date_str, time_str = data_str.split("|")
            scan_datetime = datetime.strptime(f"{date_str} {time_str}", "%d%m%Y %H%M%S")

            # User enters email
            student_email = st.text_input("Email address", placeholder="Enter your registered email address")

            if st.button("Check-in"):
                # Connect to SQLite
                conn = sqlite3.connect("attendance.db")
                cursor = conn.cursor()

                now = datetime.now(pytz.utc)
                today_date = now.date().isoformat()  # Convert to string

                # 🚨 **Check if this QR code has already been used**
                check_qr_query = """
                SELECT COUNT(*) FROM attendance 
                WHERE scan_date = ? AND scan_time = ?
                """
                cursor.execute(check_qr_query, (scan_datetime.date().isoformat(), scan_datetime.time().strftime("%H:%M:%S")))
                qr_result = cursor.fetchone()

                if qr_result[0] > 0:
                    st.error("🚫 This QR code has already been used! Please get a new one from the admin.")
                    st.image("img/lens_scan.png", width=300)
                
                else:
                    # 🚨 **Check if student has already checked in today**
                    check_student_query = """
                    SELECT COUNT(*) FROM attendance 
                    WHERE student_email = ? AND checkin_date = ?
                    """
                    cursor.execute(check_student_query, (student_email, today_date))
                    student_result = cursor.fetchone()

                    if student_result[0] > 0:
                        st.error("🚫 You have already checked in today!")
                    else:
                        # ✅ **Insert check-in record**
                        query = """
                        INSERT INTO attendance (admin_email, scan_date, scan_time, student_email, checkin_date, checkin_time) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(query, (
                            username, 
                            scan_datetime.date().isoformat(),  
                            scan_datetime.time().strftime("%H:%M:%S"),  
                            student_email, 
                            today_date,  
                            now.time().strftime("%H:%M:%S")  
                        ))

                        conn.commit()
                        st.success("✅ You have successfully checked in!")

                conn.close()  # Close connection **after handling all cases**

            st.info("📌 You can only check in once per day.")

        except (ValueError, base64.binascii.Error):
            st.error("⚠️ Invalid QR Code data.")
        
        except sqlite3.IntegrityError:
            st.error("🚫 Database constraint violation! Please contact the admin.")
            conn.rollback()  # Rollback transaction if an error occurs
            conn.close()  # Ensure connection is closed properly

    else:
        st.image("img/lens_scan.png", width=300)
        st.error("🚫 Kindly Scan a New QR Code from the Admin")



def main():
    """Main function for handling navigation."""
    if page == "ADMIN LOGIN":
        admin.admin_section()  # Call function from admin.py
    elif page == "MARK MY ATTENDANCE":
        mark_attendance()

if __name__ == "__main__":
    main()
