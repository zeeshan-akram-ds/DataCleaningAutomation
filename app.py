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
# --- After file upload ---
if uploaded_file is not None:
    df = load_file(uploaded_file)

    # --- Initialize DataCleaner once and persist in session ---
    if 'cleaner' not in st.session_state:
        st.session_state.cleaner = DataCleaner(df)
    else:
        # Update existing cleaner if a new file is uploaded
        st.session_state.cleaner.df = df

    cleaner = st.session_state.cleaner

    # --- Display preview of current dataframe ---
    st.subheader("Current Data Preview")
    st.dataframe(cleaner.df.head())

    # --- Generate and show full analysis report ---
    data_analyzer = DataAnalyzer(cleaner.df)
    report = data_analyzer.generate_report()
    display_report(report)

    # --- Generate and show recommendations ---
    re = RecommendationEngine(report)
    suggestions = re.generate_suggestions()
    display_recommendations(suggestions)

    # --- Sidebar cleaning operations ---
    st.sidebar.header("Data Cleaning Operations")

    # --- Column selection ---
    columns = cleaner.df.columns.tolist()
    selected_column = st.sidebar.selectbox("Select column for imputation", columns)

    # --- Strategy selection ---
    strategies = ['mean', 'median', 'mode', 'drop', 'constant']
    selected_strategy = st.sidebar.selectbox("Select strategy", strategies)

    # --- Optional fill value input for 'constant' strategy ---
    fill_value = None
    if selected_strategy == 'constant':
        fill_value = st.sidebar.text_input("Enter constant fill value")

    # --- Apply button ---
    if st.sidebar.button("Apply Missing Value Fix"):
        try:
            cleaner.handle_missing(selected_column, selected_strategy, fill_value=fill_value)
            st.success(f"Applied {selected_strategy} strategy to '{selected_column}' successfully.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # --- Show updated dataframe after cleaning ---
    st.subheader("Updated Data Preview")
    st.dataframe(cleaner.df.head())