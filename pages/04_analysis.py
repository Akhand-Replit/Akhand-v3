import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def analysis_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📊 ডাটা বিশ্লেষণ")

    db = Database()

    try:
        # Get occupation statistics
        occupation_stats = db.get_occupation_stats()

        if occupation_stats:
            # Convert to DataFrame for visualization
            df = pd.DataFrame(occupation_stats)

            # Total records
            total_records = df['count'].sum()
            st.metric("মোট রেকর্ড", total_records)

            # Occupation distribution
            st.subheader("পেশা অনুযায়ী বিতরণ")

            # Create pie chart
            fig = px.pie(
                df,
                values='count',
                names='পেশা',
                title='পেশা অনুযায়ী বিতরণ',
                hole=0.3
            )
            fig.update_layout(
                font=dict(family="Noto Sans Bengali"),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display table
            st.subheader("বিস্তারিত তথ্য")
            df_display = df.copy()
            df_display.columns = ['পেশা', 'সংখ্যা']
            st.dataframe(
                df_display,
                hide_index=True,
                use_container_width=True
            )

        else:
            st.info("বিশ্লেষণের জন্য কোন ডাটা পাওয়া যায়নি")

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        st.error(f"বিশ্লেষণে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    analysis_page()