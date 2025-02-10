import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def display_result_card(result, db):
    # Get batch and file information
    batch_info = db.get_batch_by_id(result['batch_id'])
    file_info = db.get_file_by_id(result['file_id']) if result['file_id'] else None

    with st.container():
        st.markdown("""
        <style>
        .result-card {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            margin-bottom: 1rem;
            border: 1px solid #dee2e6;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            # Header with name and ID
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {result['নাম']}")
            with col2:
                st.markdown(f"**ক্রমিক নং:** {result['ক্রমিক_নং']}")

            # Location info
            st.markdown(f"📍 **Location:** {batch_info['name']}" + 
                       (f" / {file_info['file_name']}" if file_info else ""))

            # Main details
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**ভোটার নং:** {result['ভোটার_নং']}")
                st.markdown(f"**পিতার নাম:** {result['পিতার_নাম']}")
                st.markdown(f"**মাতার নাম:** {result['মাতার_নাম']}")
            with col4:
                st.markdown(f"**পেশা:** {result['পেশা']}")
                st.markdown(f"**ঠিকানা:** {result['ঠিকানা']}")
                st.markdown(f"**জন্ম তারিখ:** {result['জন্ম_তারিখ']}")

            # Relationship status
            st.markdown(f"**সম্পর্কের ধরণ:** {result['relationship_status']}")

            st.markdown('</div>', unsafe_allow_html=True)

def search_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("🔍 তথ্য খুঁজুন")

    db = Database()

    # Advanced search fields
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            si_number = st.text_input("ক্রমিক নং")
            name = st.text_input("নাম")
            fathers_name = st.text_input("পিতার নং")
            mothers_name = st.text_input("মাতার নাম")

        with col2:
            occupation = st.text_input("পেশা")
            address = st.text_input("ঠিকানা")
            date_of_birth = st.text_input("জন্ম তারিখ")

    # Search buttons
    col3, col4 = st.columns([4, 1])
    with col3:
        search_button = st.button("অনুসন্ধান করুন", type="primary")
    with col4:
        show_all = st.button("সব দেখুন", type="secondary")

    if search_button or show_all:
        try:
            with st.spinner("অনুসন্ধান করা হচ্ছে..."):
                if search_button:
                    search_criteria = {
                        'ক্রমিক_নং': si_number,
                        'নাম': name,
                        'পিতার_নাম': fathers_name,
                        'মাতার_নাম': mothers_name,
                        'পেশা': occupation,
                        'ঠিকানা': address,
                        'জন্ম_তারিখ': date_of_birth
                    }
                    # Remove empty criteria
                    search_criteria = {k: v for k, v in search_criteria.items() if v}
                    results = db.search_records_advanced(search_criteria)
                else:
                    results = db.get_batch_records(None)

                if results:
                    st.success(f"{len(results)}টি ফলাফল পাওয়া গেছে")

                    # Display results in card format
                    for result in results:
                        display_result_card(result, db)
                else:
                    st.info("কোন ফলাফল পাওয়া যায়নি")

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            st.error(f"অনুসন্ধানে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    search_page()