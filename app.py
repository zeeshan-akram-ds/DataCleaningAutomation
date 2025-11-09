import streamlit as st
import pandas as pd
from core.utils import load_file, display_report, display_recommendations
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
    data_analyzer = DataAnalyzer(df)
    report = data_analyzer.generate_report()
    display_report(report)

    ## recommendations
    re = RecommendationEngine(report)
    suggestions = re.generate_suggestions()
    display_recommendations(suggestions)
