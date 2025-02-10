import streamlit as st
import pandas as pd
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

                    # Initialize session state for edited data if not exists
                    if 'edited_data' not in st.session_state:
                        st.session_state.edited_data = None

                    # Convert results to DataFrame
                    df = pd.DataFrame(results)

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
                        key="search_data_editor",
                        disabled=False
                    )

                    st.session_state.edited_data = edited_df

                    # Update button
                    if st.button("পরিবর্তনগুলি সংরক্ষণ করুন", type="primary", key="save_changes"):
                        try:
                            changes = edited_df.compare(df[[
                                'ক্রমিক_নং', 'নাম', 'ভোটার_নং', 'পিতার_নাম',
                                'মাতার_নাম', 'পেশা', 'ঠিকানা', 'জন্ম_তারিখ', 'relationship_status'
                            ]])

                            if not changes.empty:
                                for idx in changes.index:
                                    record_id = int(df.iloc[idx]['id'])
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
                                        'relationship_status': str(row_data['relationship_status']) if pd.notnull(row_data['relationship_status']) else 'Regular'
                                    }
                                    db.update_record(record_id, updated_data)

                                st.success("✅ পরিবর্তনগুলি সফলভাবে সংরক্ষিত হয়েছে!")
                                st.rerun()
                        except Exception as e:
                            logger.error(f"Update error: {str(e)}")
                            st.error(f"পরিবর্তন সংরক্ষণে সমস্যা হয়েছে: {str(e)}")

                else:
                    st.info("কোন ফলাফল পাওয়া যায়নি")

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            st.error(f"অনুসন্ধানে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    search_page()