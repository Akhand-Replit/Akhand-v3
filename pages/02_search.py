import streamlit as st
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

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
            fathers_name = st.text_input("পিতার নাম")
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
                    # Create search criteria dictionary
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
                    results = db.get_batch_records(None)  # Get all records

                if results:
                    st.success(f"{len(results)}টি ফলাফল পাওয়া গেছে")

                    for result in results:
                        with st.container():
                            st.markdown(f"""
                            <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                                <h3>{result['নাম']}</h3>
                                <p><strong>ক্রমিক নং:</strong> {result['ক্রমিক_নং']}</p>
                                <p><strong>ভোটার নং:</strong> {result['ভোটার_নং']}</p>
                                <p><strong>পিতার নাম:</strong> {result['পিতার_নাম']}</p>
                                <p><strong>মাতার নাম:</strong> {result['মাতার_নাম']}</p>
                                <p><strong>পেশা:</strong> {result['পেশা']}</p>
                                <p><strong>ঠিকানা:</strong> {result['ঠিকানা']}</p>
                                <p><strong>ফাইল:</strong> {result['batch_name']}/{result['file_name']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("কোন ফলাফল পাওয়া যায়নি")

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            st.error(f"অনুসন্ধানে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    search_page()