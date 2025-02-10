import streamlit as st
import pandas as pd
import numpy as np
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

    # Get all batches
    batches = db.get_all_batches()

    if not batches:
        st.info("কোন ডাটা পাওয়া যায়নি")
        return

    # Initialize session state for delete confirmation
    if 'confirm_delete_all' not in st.session_state:
        st.session_state.confirm_delete_all = False

    # Clear all data button with confirmation dialog
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("সব ডাটা মুছুন", type="secondary"):
            st.session_state.confirm_delete_all = True

    # Show confirmation dialog
    if st.session_state.confirm_delete_all:
        st.warning("""
        ⚠️ সতর্কতা!
        আপনি কি নিশ্চিত যে আপনি সমস্ত ডেটা মুছে ফেলতে চান?
        এই কাজটি অপরিবর্তনীয়!
        """)

        confirm_col1, confirm_col2 = st.columns(2)
        with confirm_col1:
            if st.button("হ্যাঁ, সব মুছে ফেলুন", type="primary", use_container_width=True):
                try:
                    db.clear_all_data()
                    st.success("✅ সমস্ত ডেটা সফলভাবে মুছে ফেলা হয়েছে")
                    st.session_state.confirm_delete_all = False
                    st.rerun()
                except Exception as e:
                    logger.error(f"Clear data error: {str(e)}")
                    st.error(f"❌ ডেটা মুছে ফেলার সময় সমস্যা হয়েছে: {str(e)}")

        with confirm_col2:
            if st.button("না, বাতিল করুন", type="secondary", use_container_width=True):
                st.session_state.confirm_delete_all = False
                st.rerun()

    # Batch selection
    with col1:
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

            # Show total count
            st.write(f"মোট রেকর্ড: {len(records)}")

            # Create editable dataframe
            edited_df = st.data_editor(
                df[[
                    'ক্রমিক_নং', 'নাম', 'ভোটার_নং', 'পিতার_নাম',
                    'মাতার_নাম', 'পেশা', 'ঠিকানা', 'জন্ম_তারিখ', 'relationship_status'
                ]],
                column_config={
                    'ক্রমিক_নং': st.column_config.TextColumn('ক্রমিক নং'),
                    'নাম': st.column_config.TextColumn('নাম'),
                    'ভোটার_নং': st.column_config.TextColumn('ভোটার নং'),
                    'পিতার_নাম': st.column_config.TextColumn('পিতার নাম'),
                    'মাতার_নাম': st.column_config.TextColumn('মাতার নাম'),
                    'পেশা': st.column_config.TextColumn('পেশা'),
                    'ঠিকানা': st.column_config.TextColumn('ঠিকানা'),
                    'জন্ম_তারিখ': st.column_config.TextColumn('জন্ম তারিখ'),
                    'relationship_status': st.column_config.SelectboxColumn(
                        'সম্পর্কের ধরণ',
                        options=['Regular', 'Friend', 'Enemy'],
                        required=True,
                        default='Regular'
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="data_editor"
            )

            # Update button
            if st.button("পরিবর্তনগুলি সংরক্ষণ করুন", type="primary"):
                try:
                    # Compare and update changed records
                    changes = edited_df.compare(df[[
                        'ক্রমিক_নং', 'নাম', 'ভোটার_নং', 'পিতার_নাম',
                        'মাতার_নাম', 'পেশা', 'ঠিকানা', 'জন্ম_তারিখ', 'relationship_status'
                    ]])

                    if not changes.empty:
                        for idx in changes.index:
                            record_id = int(df.iloc[idx]['id'])  # Convert to native Python int
                            # Convert DataFrame row to dictionary with proper type conversion
                            row_data = edited_df.iloc[idx]
                            updated_data = {
                                'ক্রমিক_নং': str(row_data['ক্রমিক_নং']) if pd.notnull(row_data['ক্রমিক_নং']) else '',
                                'নাম': str(row_data['নাম']) if pd.notnull(row_data['নাম']) else '',
                                'ভোটার_নং': str(row_data['ভোটার_নং']) if pd.notnull(row_data['ভোটার_নং']) else '',
                                'পিতার_নাম': str(row_data['পিতার_নাম']) if pd.notnull(row_data['পিতার_নাম']) else '',
                                'মাতার_নাম': str(row_data['মাতার_নাম']) if pd.notnull(row_data['মাতার_নাম']) else '',
                                'পেশা': str(row_data['পেশা']) if pd.notnull(row_data['পেশা']) else '',
                                'ঠিকানা': str(row_data['ঠিকানা']) if pd.notnull(row_data['ঠিকানা']) else '',
                                'জন্ম_তারিখ': str(row_data['জন্ম_তারিখ']) if pd.notnull(row_data['জন্ম_তারিখ']) else '',
                                'relationship_status': str(row_data['relationship_status']) if pd.notnull(row_data['relationship_status']) else ''

                            }
                            db.update_record(record_id, updated_data)

                        st.success("পরিবর্তনগুলি সফলভাবে সংরক্ষিত হয়েছে!")
                        st.rerun()
                except Exception as e:
                    logger.error(f"Update error: {str(e)}")
                    st.error(f"পরিবর্তন সংরক্ষণে সমস্যা হয়েছে: {str(e)}")
        else:
            st.info("কোন রেকর্ড পাওয়া যায়নি")
    else:
        st.info("এই ব্যাচে কোন ফাইল নেই")

if __name__ == "__main__":
    all_data_page()