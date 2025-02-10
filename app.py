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
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("লগ আউট", type="secondary"):
                logout()
                st.rerun()

        with col1:
            st.title("ডাটা ম্যানেজমেন্ট সিস্টেম")

        # Sample data for demonstration
        sample_data = {
            'serial_no': '৫২০',
            'record_no': '০০০০৬৫০৯৯৮৮৬',
            'father_name': 'সাধারণিল',
            'mother_name': 'মঞ্জুতাজ',
            'occupation': 'পুলিশ',
            'address': 'কাঠালী, শ্রীপুর, গাজীপুর',
            'phone': '0544585',
            'facebook_url': 'https://www.facebook.com/help/104002523024878/'
        }

        display_profile_card(sample_data)

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