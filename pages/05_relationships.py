import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def relationships_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("👥 বন্ধু এবং শত্রু তালিকা")

    db = Database()

    # Create tabs for Friend and Enemy lists
    tab1, tab2 = st.tabs(["বন্ধু তালিকা", "শত্রু তালিকা"])

    with tab1:
        st.subheader("🤝 বন্ধু তালিকা")
        friends = db.get_relationship_records('Friend')
        if friends:
            for friend in friends:
                with st.container():
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                        <h3>{friend['নাম']}</h3>
                        <p><strong>ক্রমিক নং:</strong> {friend['ক্রমিক_নং']}</p>
                        <p><strong>ভোটার নং:</strong> {friend['ভোটার_নং']}</p>
                        <p><strong>পিতার নাম:</strong> {friend['পিতার_নাম']}</p>
                        <p><strong>মাতার নাম:</strong> {friend['মাতার_নাম']}</p>
                        <p><strong>পেশা:</strong> {friend['পেশা']}</p>
                        <p><strong>ঠিকানা:</strong> {friend['ঠিকানা']}</p>
                        <p><strong>ফাইল:</strong> {friend['batch_name']}/{friend['file_name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Regular এ ফিরিয়ে নিন", key=f"remove_friend_{friend['id']}", type="secondary"):
                        db.update_relationship_status(friend['id'], 'Regular')
                        st.success("✅ Regular হিসেবে আপডেট করা হয়েছে!")
                        st.rerun()
        else:
            st.info("কোন বন্ধু যোগ করা হয়নি")

    with tab2:
        st.subheader("⚔️ শত্রু তালিকা")
        enemies = db.get_relationship_records('Enemy')
        if enemies:
            for enemy in enemies:
                with st.container():
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                        <h3>{enemy['নাম']}</h3>
                        <p><strong>ক্রমিক নং:</strong> {enemy['ক্রমিক_নং']}</p>
                        <p><strong>ভোটার নং:</strong> {enemy['ভোটার_নং']}</p>
                        <p><strong>পিতার নাম:</strong> {enemy['পিতার_নাম']}</p>
                        <p><strong>মাতার নাম:</strong> {enemy['মাতার_নাম']}</p>
                        <p><strong>পেশা:</strong> {enemy['পেশা']}</p>
                        <p><strong>ঠিকানা:</strong> {enemy['ঠিকানা']}</p>
                        <p><strong>ফাইল:</strong> {enemy['batch_name']}/{enemy['file_name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Regular এ ফিরিয়ে নিন", key=f"remove_enemy_{enemy['id']}", type="secondary"):
                        db.update_relationship_status(enemy['id'], 'Regular')
                        st.success("✅ Regular হিসেবে আপডেট করা হয়েছে!")
                        st.rerun()
        else:
            st.info("কোন শত্রু যোগ করা হয়নি")

if __name__ == "__main__":
    relationships_page()