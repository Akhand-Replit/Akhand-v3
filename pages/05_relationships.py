import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
apply_custom_styling()

def display_relationship_card(record):
    # Create a flex container for name and photo
    photo_html = f"""<img src="{record.get('photo_link', '')}" 
                     style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%; margin-right: 1rem;"
                     onerror="this.style.display='none'"
                     alt="{record['নাম']} এর ছবি">""" if record.get('photo_link') else ""

    st.markdown(f"""
    <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            {photo_html}
            <h3 style='margin: 0;'>{record['নাম']}</h3>
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
            <div>
                <p><strong>ক্রমিক নং:</strong> {record['ক্রমিক_নং']}</p>
                <p><strong>ভোটার নং:</strong> {record['ভোটার_নং']}</p>
                <p><strong>পিতার নাম:</strong> {record['পিতার_নাম']}</p>
                <p><strong>মাতার নাম:</strong> {record['মাতার_নাম']}</p>
                <p><strong>পেশা:</strong> {record['পেশা']}</p>
                <p><strong>ঠিকানা:</strong> {record['ঠিকানা']}</p>
            </div>
            <div>
                <p><strong>ফোন নম্বর:</strong> {record.get('phone_number', '')}</p>
                <p><strong>ফেসবুক:</strong> <a href="{record.get('facebook_link', '#')}" target="_blank">{record.get('facebook_link', '')}</a></p>
                <p><strong>বিবরণ:</strong> {record.get('description', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
            # Get batch ID
            batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)
            records = [r for r in db.get_relationship_records(relationship_type) 
                      if r['batch_id'] == batch_id]

        if not records:
            st.info(f"কোন {'বন্ধু' if relationship_type == 'Friend' else 'শত্রু' if relationship_type == 'Enemy' else 'সংযুক্ত ব্যক্তি'} যোগ করা হয়নি")
            return

        # Show total count
        st.write(f"মোট: {len(records)}")

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
                    display_relationship_card(record)
                    if st.button(
                        "🔄 Regular এ ফিরিয়ে নিন", 
                        key=f"remove_{relationship_type}_{record['id']}", 
                        type="secondary",
                        use_container_width=True
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

    with tab3:
        st.subheader("🔗 সংযুক্ত তালিকা")
        display_relationship_section('Connected')

if __name__ == "__main__":
    relationships_page()