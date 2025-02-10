import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
apply_custom_styling()

def display_relationship_card(record):
    st.markdown(f"""
    <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
        <h3>{record['নাম']}</h3>
        <p><strong>ক্রমিক নং:</strong> {record['ক্রমিক_নং']}</p>
        <p><strong>ভোটার নং:</strong> {record['ভোটার_নং']}</p>
        <p><strong>পিতার নাম:</strong> {record['পিতার_নাম']}</p>
        <p><strong>মাতার নাম:</strong> {record['মাতার_নাম']}</p>
        <p><strong>পেশা:</strong> {record['পেশা']}</p>
        <p><strong>ঠিকানা:</strong> {record['ঠিকানা']}</p>
    </div>
    """, unsafe_allow_html=True)

def relationships_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("👥 বন্ধু এবং শত্রু তালিকা")

    db = Database()

    # Create tabs for Friend and Enemy lists
    tab1, tab2 = st.tabs(["বন্ধু তালিকা", "শত্রু তালিকা"])

    def display_relationship_section(relationship_type):
        records = db.get_relationship_records(relationship_type)
        if not records:
            st.info(f"কোন {'বন্ধু' if relationship_type == 'Friend' else 'শত্রু'} যোগ করা হয়নি")
            return

        # Group records by batch and file
        batch_file_groups = defaultdict(lambda: defaultdict(list))
        for record in records:
            batch_file_groups[record['batch_name']][record['file_name']].append(record)

        # Display in folder structure without nested expanders
        for batch_name in sorted(batch_file_groups.keys()):
            st.markdown(f"### 📁 ব্যাচ: {batch_name}")
            files = batch_file_groups[batch_name]

            for file_name in sorted(files.keys()):
                st.markdown(f"#### 📄 ফাইল: {file_name}")
                records = files[file_name]

                # Add a visual separator
                st.markdown("""<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #eee;">""", unsafe_allow_html=True)

                for record in records:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        display_relationship_card(record)
                    with col2:
                        if st.button(
                            "🔄 Regular এ ফিরিয়ে নিন", 
                            key=f"remove_{relationship_type}_{record['id']}", 
                            type="secondary"
                        ):
                            db.update_relationship_status(record['id'], 'Regular')
                            st.success("✅ Regular হিসেবে আপডেট করা হয়েছে!")
                            st.rerun()

                # Add spacing between files
                st.markdown("<br>", unsafe_allow_html=True)

    with tab1:
        st.subheader("🤝 বন্ধু তালিকা")
        display_relationship_section('Friend')

    with tab2:
        st.subheader("⚔️ শত্রু তালিকা")
        display_relationship_section('Enemy')

if __name__ == "__main__":
    relationships_page()