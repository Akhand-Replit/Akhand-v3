import os
import sys
import streamlit as st
import logging
import pandas as pd

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

def display_data_card(data):
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### বন্ধু তালিকা")
            st.markdown(f"**ক্রমিক নং:** {data.get('serial_no', '')}")
            st.markdown(f"**রেকর্ড নং:** {data.get('record_no', '')}")
            st.markdown(f"**বিভাগের নাম:** {data.get('division_name', '')}")
            st.markdown(f"**স্থানের নাম:** {data.get('location_name', '')}")
            st.markdown(f"**ঠিকানা:** {data.get('address', '')}")

        with col2:
            st.markdown("### যোগাযোগ")
            st.markdown(f"**ফোন নাম্বার:** {data.get('phone', '')}")
            if data.get('facebook'):
                st.markdown(f"**ফেসবুক:** [{data.get('facebook', '')}]({data.get('facebook_url', '#')})")

def main():
    # Show logout button if authenticated
    if st.session_state.authenticated:
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("লগ আউট", type="secondary"):
                logout()
                st.rerun()

        with col1:
            st.title("ডাটা ম্যানেজমেন্ট সিস্টেম")

        # Sample data for demonstration
        sample_data = {
            'serial_no': '৫২৫',
            'record_no': '৫৩০৬৫৫৯৯৯৯৮৮',
            'division_name': 'সড়ক চট্ট হাই',
            'location_name': 'লীলা স্বামী বর্ণন',
            'address': 'কক্সবাজার, শ্রীপুর',
            'phone': '',
            'facebook': 'ফেসবুক'
        }

        display_data_card(sample_data)

        st.markdown("""
        ### মূল মেনু
        - 📤 **আপলোড পেজ**: নতুন ফাইল আপলোড করুন
        - 🔍 **সার্চ পেজ**: তথ্য খুঁজুন
        - 📁 **সব তথ্য**: সকল সংরক্ষিত তথ্য দেখুন
        - 📊 **বিশ্লেষণ**: ডাটা বিশ্লেষণ দেখুন
        """)

    else:
        login_form()

if __name__ == "__main__":
    main()