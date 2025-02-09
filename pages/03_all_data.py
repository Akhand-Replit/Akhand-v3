import streamlit as st
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

    # Display batches and their records
    for batch in batches:
        with st.expander(f"ব্যাচ: {batch['name']} ({batch['created_at'].strftime('%Y-%m-%d %H:%M')})"):
            records = db.get_batch_records(batch['id'])

            if records:
                st.write(f"মোট রেকর্ড: {len(records)}")

                # Display records in a clean format
                for record in records:
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                        <h4>{record['নাম']}</h4>
                        <p><strong>ক্রমিক নং:</strong> {record['ক্রমিক_নং']}</p>
                        <p><strong>ভোটার নং:</strong> {record['ভোটার_নং']}</p>
                        <p><strong>পিতার নাম:</strong> {record['পিতার_নাম']}</p>
                        <p><strong>মাতার নাম:</strong> {record['মাতার_নাম']}</p>
                        <p><strong>পেশা:</strong> {record['পেশা']}</p>
                        <p><strong>ঠিকানা:</strong> {record['ঠিকানা']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("এই ব্যাচে কোন রেকর্ড নেই")

if __name__ == "__main__":
    all_data_page()