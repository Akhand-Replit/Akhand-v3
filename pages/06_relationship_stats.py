import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def get_relationship_stats(db):
    """Get statistics for all relationship statuses"""
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT relationship_status, COUNT(*) as count
            FROM records
            GROUP BY relationship_status
            ORDER BY count DESC
        """)
        return cur.fetchall()

def get_batch_relationship_stats(db):
    """Get relationship statistics per batch"""
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT b.name as batch_name, r.relationship_status, COUNT(*) as count
            FROM records r
            JOIN batches b ON r.batch_id = b.id
            GROUP BY b.name, r.relationship_status
            ORDER BY b.name, r.relationship_status
        """)
        return cur.fetchall()

def relationship_stats_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📊 সম্পর্কের পরিসংখ্যান")
    
    db = Database()
    
    # Get overall statistics
    stats = get_relationship_stats(db)
    if not stats:
        st.info("কোন পরিসংখ্যান পাওয়া যায়নি")
        return
        
    # Create DataFrame for overall stats
    df_stats = pd.DataFrame(stats, columns=['relationship_status', 'count'])
    
    # Display pie chart for overall distribution
    st.subheader("📊 সামগ্রিক সম্পর্কের বিতরণ")
    fig_pie = px.pie(
        df_stats,
        values='count',
        names='relationship_status',
        title='সম্পর্কের ধরণ অনুযায়ী বিতরণ',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Display summary statistics
    st.subheader("📑 সারসংক্ষেপ")
    total = df_stats['count'].sum()
    
    # Create three columns for statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("মোট", total)
    
    for status, count in zip(df_stats['relationship_status'], df_stats['count']):
        if status == 'Regular':
            with col2:
                st.metric("নিয়মিত", count)
        elif status == 'Friend':
            with col3:
                st.metric("বন্ধু", count)
        elif status == 'Enemy':
            with col4:
                st.metric("শত্রু", count)
    
    # Get and display batch-wise statistics
    batch_stats = get_batch_relationship_stats(db)
    if batch_stats:
        st.subheader("📊 ব্যাচ অনুযায়ী সম্পর্কের বিতরণ")
        df_batch_stats = pd.DataFrame(batch_stats, columns=['batch_name', 'relationship_status', 'count'])
        
        # Create grouped bar chart
        fig_bar = px.bar(
            df_batch_stats,
            x='batch_name',
            y='count',
            color='relationship_status',
            title='ব্যাচ অনুযায়ী সম্পর্কের বিতরণ',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_bar.update_layout(
            xaxis_title="ব্যাচের নাম",
            yaxis_title="সংখ্যা",
            legend_title="সম্পর্কের ধরণ"
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Display detailed table
        st.subheader("📋 বিস্তারিত পরিসংখ্যান")
        pivot_table = df_batch_stats.pivot(
            index='batch_name',
            columns='relationship_status',
            values='count'
        ).fillna(0).astype(int)
        
        pivot_table['মোট'] = pivot_table.sum(axis=1)
        st.dataframe(pivot_table, use_container_width=True)

if __name__ == "__main__":
    relationship_stats_page()
