import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
apply_custom_styling()

def get_record_location(db, record):
    """Get batch and file information for a record"""
    batch_info = db.get_batch_by_id(record['batch_id'])
    file_info = db.get_file_by_id(record.get('file_id'))

    location = batch_info['name'] if batch_info else 'Unknown Batch'
    if file_info and file_info.get('name'):
        location += f" / {file_info['name']}"

    return location

def display_relationship_card(record, db):
    """Display a single relationship card with profile image and details"""
    with st.container():
        # Profile section with image and basic info
        cols = st.columns([1, 3])

        with cols[0]:
            # Profile image
            if record.get('photo_link'):
                st.image(record['photo_link'], width=100)

        with cols[1]:
            st.markdown(f"### {record.get('নাম', '')}")

        # Main information grid
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **ক্রমিক নং:** {record.get('ক্রমিক_নং', '')}\n
            **রেকর্ড নং:** {record.get('ভোটার_নং', '')}\n
            **পিতার নাম:** {record.get('পিতার_নাম', '')}\n
            **মাতার নাম:** {record.get('মাতার_নাম', '')}\n
            **পেশা:** {record.get('পেশা', '')}\n
            **ঠিকানা:** {record.get('ঠিকানা', '')}
            """)

        with col2:
            st.markdown(f"""
            **ফোন নাম্বার:** {record.get('phone_number', '')}\n
            **ফেসবুক:**""")
            if record.get('facebook_link'):
                st.markdown(f"[{record.get('facebook_link', '')}]({record.get('facebook_link', '')})")

            # Add location information under বিবরণ
            location = get_record_location(db, record)
            st.markdown(f"**বিবরণ:** {location}")

    # Add action button below the card
    if st.button(
        "🔄 Regular এ ফিরিয়ে নিন", 
        key=f"remove_{record['id']}", 
        type="secondary",
        use_container_width=True
    ):
        db.update_relationship_status(record['id'], 'Regular')
        st.success("✅ Regular হিসেবে আপডেট করা হয়েছে!")
        st.rerun()

def relationships_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("👥 বন্ধু এবং শত্রু তালিকা")

    db = Database()

    # Get all batches
    batches = db.get_all_batches()

    if not batches:
        st.info("কোন ডাটা পাওয়া যায়নি")
        return

    # Batch selection
    selected_batch = st.selectbox(
        "ব্যাচ নির্বাচন করুন",
        options=['সব ব্যাচ'] + [batch['name'] for batch in batches],
        format_func=lambda x: f"ব্যাচ: {x}"
    )

    # Create tabs for Friend, Enemy and Connected lists
    tab1, tab2, tab3 = st.tabs(["বন্ধু তালিকা", "শত্রু তালিকা", "সংযুক্ত তালিকা"])

    def display_relationship_section(relationship_type):
        # Get records based on selection
        if selected_batch == 'সব ব্যাচ':
            records = db.get_relationship_records(relationship_type)
        else:
            batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)
            records = [r for r in db.get_relationship_records(relationship_type) 
                      if r['batch_id'] == batch_id]

        if not records:
            st.info(f"কোন {'বন্ধু' if relationship_type == 'Friend' else 'শত্রু' if relationship_type == 'Enemy' else 'সংযুক্ত ব্যক্তি'} যোগ করা হয়নি")
            return

        # Show total count
        st.write(f"মোট: {len(records)}")

        # Display each record in a card format
        for record in records:
            display_relationship_card(record, db)

    with tab1:
        st.subheader("🤝 বন্ধু তালিকা")
        display_relationship_section('Friend')

    with tab2:
        st.subheader("⚔️ শত্রু তালিকা")
        display_relationship_section('Enemy')

    with tab3:
        st.subheader("🔗 সংযুক্ত তালিকা")
        display_relationship_section('Connected')

if __name__ == "__main__":
    relationships_page()