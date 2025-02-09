import os
import sys
import streamlit as st
import logging

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