import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def all_data_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📁 সব তথ্য")

    db = Database()

    # Clear all data button with confirmation
    if st.sidebar.button("সব ডাটা মুছে ফেলুন", type="secondary"):
        if st.sidebar.checkbox("আপনি কি নিশ্চিত? এই কাজটি অপরিবর্তনীয়!"):
            try:
                db.clear_all_data()
                st.sidebar.success("সব ডাটা সফলভাবে মুছে ফেলা হয়েছে")
                st.rerun()
            except Exception as e:
                logger.error(f"Clear data error: {str(e)}")
                st.sidebar.error(f"ডাটা মুছতে সমস্যা হয়েছে: {str(e)}")

    # Get all batches
    batches = db.get_all_batches()

    if not batches:
        st.info("কোন ডাটা পাওয়া যায়নি")
        return

    # Batch selection
    selected_batch = st.selectbox(
        "ব্যাচ নির্বাচন করুন",
        options=[batch['name'] for batch in batches],
        format_func=lambda x: f"ব্যাচ: {x}"
    )

    # Get selected batch details
    selected_batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)

    # Get files for selected batch
    files = db.get_batch_files(selected_batch_id)

    if files:
        selected_file = st.selectbox(
            "ফাইল নির্বাচন করুন",
            options=['সব'] + [file['file_name'] for file in files],
            format_func=lambda x: f"ফাইল: {x}" if x != 'সব' else "সব ফাইল দেখুন"
        )

        # Get records based on selection
        if selected_file == 'সব':
            records = db.get_batch_records(selected_batch_id)
        else:
            records = db.get_file_records(selected_batch_id, selected_file)

        if records:
            # Convert records to DataFrame
            df = pd.DataFrame(records)

            # Reorder and rename columns for display
            display_columns = [
                'ক্রমিক_নং', 'নাম', 'ভোটার_নং', 'পিতার_নাম', 
                'মাতার_নাম', 'পেশা', 'ঠিকানা', 'জন্ম_তারিখ',
                'file_name'
            ]

            column_names = {
                'ক্রমিক_নং': 'ক্রমিক নং',
                'নাম': 'নাম',
                'ভোটার_নং': 'ভোটার নং',
                'পিতার_নাম': 'পিতার নাম',
                'মাতার_নাম': 'মাতার নাম',
                'পেশা': 'পেশা',
                'ঠিকানা': 'ঠিকানা',
                'জন্ম_তারিখ': 'জন্ম তারিখ',
                'file_name': 'ফাইল'
            }

            df_display = df[display_columns].rename(columns=column_names)

            # Show total count
            st.write(f"মোট রেকর্ড: {len(records)}")

            # Display as table with editing capability
            st.dataframe(
                df_display,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("কোন রেকর্ড পাওয়া যায়নি")
    else:
        st.info("এই ব্যাচে কোন ফাইল নেই")

if __name__ == "__main__":
    all_data_page()