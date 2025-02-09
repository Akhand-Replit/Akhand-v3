import streamlit as st

def apply_custom_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;700&display=swap');
        
        /* Global font settings */
        * {
            font-family: 'Noto Sans Bengali', sans-serif;
        }
        
        /* Header styling */
        .stTitle {
            font-weight: bold;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f2f6;
        }
        
        /* Card styling */
        .stBlock {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
        .stButton button {
            width: 100%;
            border-radius: 0.3rem;
            font-weight: 500;
        }
        
        /* Search box styling */
        .stTextInput input {
            border-radius: 0.3rem;
        }
        
        /* Table styling */
        .stDataFrame {
            border: 1px solid #f0f2f6;
            border-radius: 0.5rem;
        }
        
        /* Alert/message styling */
        .stAlert {
            padding: 1rem;
            border-radius: 0.3rem;
        }
        </style>
    """, unsafe_allow_html=True)
