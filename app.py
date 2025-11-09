import streamlit as st
import pandas as pd
from core.utils import load_file
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.cleaner import DataCleaner
from core.recommender import RecommendationEngine


st.set_page_config("Data Cleaning Assistance")

st.title("Data Cleaning Pro")

uploaded_file = st.sidebar.file_uploader(label="Upload csv or excel file", type=['csv','xlsx'])
if uploaded_file is not None:
    df = load_file(uploaded_file)
    st.dataframe(df.head())