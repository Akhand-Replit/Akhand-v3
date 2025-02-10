import os
import sys
import streamlit as st
import logging
import pandas as pd
from psycopg2 import sql
import psycopg2

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from attached_assets.auth import init_auth, login_form, logout
from utils.styling import apply_custom_styling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="ডাটা ম্যানেজমেন্ট সিস্টেম",
    page_icon="📊",
    layout="wide"
)

# Apply custom styling
apply_custom_styling()

# Initialize authentication
init_auth()

def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_batch_statistics():
    conn = get_db_connection()
    if not conn:
        return {
            "total_batches": 0,
            "total_files": 0,
            "recent_batch": "কোন ব্যাচ নেই",
            "processed_data": 0
        }

    try:
        cur = conn.cursor()

        # Get total number of batches
        cur.execute("SELECT COUNT(DISTINCT batch_id) FROM data_batches")
        total_batches = cur.fetchone()[0] or 0

        # Get total number of files
        cur.execute("SELECT COUNT(*) FROM data_files")
        total_files = cur.fetchone()[0] or 0

        # Get most recent batch
        cur.execute("""
            SELECT batch_name 
            FROM data_batches 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        recent_batch = cur.fetchone()
        recent_batch = recent_batch[0] if recent_batch else "কোন ব্যাচ নেই"

        # Get total processed records
        cur.execute("SELECT COUNT(*) FROM processed_data")
        processed_data = cur.fetchone()[0] or 0

        return {
            "total_batches": total_batches,
            "total_files": total_files,
            "recent_batch": recent_batch,
            "processed_data": processed_data
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return {
            "total_batches": 0,
            "total_files": 0,
            "recent_batch": "ত্রুটি",
            "processed_data": 0
        }
    finally:
        if conn:
            conn.close()

def display_profile_card(data):
    with st.container():
        # Profile section with image and basic info
        cols = st.columns([1, 3])

        with cols[0]:
            # Profile image
            st.image("https://placekitten.com/100/100", width=100)

        with cols[1]:
            st.markdown("### বিস্তৃতি")

        # Main information grid
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **ক্রমিক নং:** {data.get('serial_no', '')}\n
            **রেকর্ড নং:** {data.get('record_no', '')}\n
            **পিতার নাম:** {data.get('father_name', '')}\n
            **মাতার নাম:** {data.get('mother_name', '')}\n
            **পেশা:** {data.get('occupation', '')}\n
            **ঠিকানা:** {data.get('address', '')}
            """)

        with col2:
            st.markdown(f"""
            **ফোন নাম্বার:** {data.get('phone', '')}\n
            **ফেসবুক:**""")
            if data.get('facebook_url'):
                st.markdown(f"[{data.get('facebook_url', '')}]({data.get('facebook_url', '')})")
            st.markdown("**বিবরণ:**")


def main():
    # Show logout button if authenticated
    if st.session_state.authenticated:
        # Header section with logout button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("লগ আউট", type="secondary"):
                logout()
                st.rerun()

        with col1:
            st.title("ডাটা ম্যানেজমেন্ট সিস্টেম")

        # Description section
        st.markdown("""
        ### সিস্টেম বর্ণনা
        এই ডাটা ম্যানেজমেন্ট সিস্টেমটি বাংলা টেক্সট প্রসেসিং এবং ডাটা বিশ্লেষণের জন্য একটি সমন্বিত প্ল্যাটফর্ম। 
        এটি মাল্টিলিঙ্গুয়াল সম্পর্ক ট্র্যাকিং, উন্নত সার্চ এবং ফিল্টারিং সুবিধা প্রদান করে।
        """)

        # Dashboard Statistics
        st.markdown("### ড্যাশবোর্ড")
        stats = get_batch_statistics()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("মোট ব্যাচ", f"{stats['total_batches']}")
        with col2:
            st.metric("মোট ফাইল", f"{stats['total_files']}")
        with col3:
            st.metric("সর্বশেষ ব্যাচ", stats['recent_batch'])
        with col4:
            st.metric("প্রক্রিয়াকৃত ডাটা", f"{stats['processed_data']}")

        # User Guide
        st.markdown("""
        ### ব্যবহার নির্দেশিকা

        ১. **ডাটা আপলোড**
        - 📤 "আপলোড পেজ" এ ক্লিক করুন
        - ফাইল নির্বাচন করুন
        - "আপলোড" বাটনে ক্লিক করুন

        ২. **ডাটা অনুসন্ধান**
        - 🔍 "সার্চ পেজ" এ যান
        - অনুসন্ধান ফিল্টার ব্যবহার করুন
        - ফলাফল দেখুন

        ৩. **ডাটা বিশ্লেষণ**
        - 📊 "বিশ্লেষণ" ট্যাবে যান
        - রিপোর্ট জেনারেট করুন
        - স্ট্যাটিসটিক্স দেখুন
        """)


        # Main Menu
        st.markdown("### মূল মেনু")
        menu_col1, menu_col2 = st.columns(2)

        with menu_col1:
            st.markdown("""
            - 📤 **আপলোড পেজ**: নতুন ফাইল আপলোড করুন
            - 🔍 **সার্চ পেজ**: তথ্য খুঁজুন
            """)

        with menu_col2:
            st.markdown("""
            - 📁 **সব তথ্য**: সকল সংরক্ষিত তথ্য দেখুন
            - 📊 **বিশ্লেষণ**: ডাটা বিশ্লেষণ দেখুন
            """)

    else:
        login_form()

if __name__ == "__main__":
    main()