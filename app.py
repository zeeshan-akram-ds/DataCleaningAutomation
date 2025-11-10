import streamlit as st
import pandas as pd
from core.utils import load_file, display_report, display_recommendations, get_categorical_columns, get_numeric_columns
from core.analyzer import DataAnalyzer
from core.visualizer import DataVisualizer
from core.cleaner import DataCleaner
from core.recommender import RecommendationEngine
import io


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
    # Initialize DataVisualizer once
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = DataVisualizer(st.session_state.cleaner.df)
    else:
        st.session_state.visualizer.df = st.session_state.cleaner.df

    cleaner = st.session_state.cleaner

    # --- Display preview of current dataframe ---
    st.subheader("Current Data Preview")
    st.dataframe(cleaner.df.head())

    # --- Generate and show full analysis report ---
    data_analyzer = DataAnalyzer(cleaner.df)
    report = data_analyzer.generate_report()

    # --- Generate and show recommendations ---
    re = RecommendationEngine(report)
    suggestions = re.generate_suggestions()

    ## Tabs for tasks
    report_tab, visualize_tab, download_tab = st.tabs(["Analysis Report", "Visualize Data", "Download Cleaned Data"])

    with report_tab:
        # report
        display_report(report)

        # suggestions
        display_recommendations(suggestions)
        # data preview

    with visualize_tab:
        st.subheader("Generate Visualizations")
        plots_list = ["Correlation Heatmap", "Missing Value Heatmap", "Value Counts", "plot outliers", "pairplot"]
        selected_plot = st.selectbox("Choose plot to generate", plots_list, key='plot_generation')
        visualizer = st.session_state.visualizer

        if selected_plot == 'Correlation Heatmap':
            if st.button("Generate Heatmap", key='heatmap'):
                visualizer.plot_correlation_heatmap(file_path='temp.png')
                st.image("temp.png", use_column_width=True)
        elif selected_plot == 'Missing Value Heatmap':
            if st.button("Generate Missing Values Heatmap"):
                visualizer.plot_missing_heatmap(file_path='temp.png')
                st.image("temp.png", use_column_width=True)
        elif selected_plot == 'Value Counts':
            cat_cols = get_categorical_columns(st.session_state.cleaner.df)
            selected_col = st.selectbox("select column to plot", cat_cols, key='column_selection')
            if st.button("Generate Countplot"):
                visualizer.plot_value_counts(selected_col, file_path='temp.png')
                st.image('temp.png', use_column_width=True)
        elif selected_plot == 'plot outliers':
            numeric_cols = get_numeric_columns(st.session_state.cleaner.df)
            selected_col = st.selectbox("select column to plot", numeric_cols, key='numeric_column_selection')
            if st.button("Generate BoxPlot"):
                visualizer.plot_outliers(selected_col, file_path='temp.png')
                st.image('temp.png', use_column_width=True)
        elif selected_plot == 'pairplot':
            numeric_cols = get_numeric_columns(st.session_state.cleaner.df)
            subset = st.multiselect("select columns for pairplot", numeric_cols, key='cols_for_pairplot', default=numeric_cols[0:2])
            if len(subset) < 2:
                st.error("Please select at least two columns to create a pairplot.")
            else:
                if st.button("Generate Pairplot"):
                    visualizer.pairplot_numeric(file_path='temp.png', subset=subset)
                    st.image('temp.png', use_column_width=True)
        else:
            print("Select from available plots.")

    with download_tab:
        st.subheader("Download Cleaned Data")

        file_format = st.selectbox("Choose file format", ["CSV", "Excel"])

        if file_format == "CSV":
            # Create CSV data in memory
            csv_data = st.session_state.cleaner.df.to_csv(index=False).encode('utf-8')

            # Download button for CSV
            st.download_button(
                label="Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )

        elif file_format == "Excel":
            # Create Excel data in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.cleaner.df.to_excel(writer, index=False, sheet_name='CleanedData')
            excel_data = output.getvalue()

            # Download button for Excel
            st.download_button(
                label="Download Cleaned Data",
                data=excel_data,
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- Sidebar cleaning operations ---
    st.sidebar.header("Data Cleaning Operations")

    # --- Column selection ---
    columns = cleaner.df.columns.tolist()
    selected_column = st.sidebar.selectbox("Select column for Imputation", columns, key='missing_value_col_sel')

    # --- Strategy selection ---
    strategies = ['mean', 'median', 'mode', 'drop', 'constant']
    selected_strategy = st.sidebar.selectbox("Select strategy", strategies, key='missing_strategy_sel')

    # --- Optional fill value input for 'constant' strategy ---
    fill_value = None
    if selected_strategy == 'constant':
        fill_value = st.sidebar.text_input("Enter constant fill value")

    # --- Apply button ---
    if st.sidebar.button("Apply Missing Value Fix", key='fill missing'):
        try:
            cleaner.handle_missing(selected_column, selected_strategy, fill_value=fill_value)
            st.success(f"Applied {selected_strategy} strategy to '{selected_column}' successfully.")
            # --- Show updated dataframe after cleaning ---
            with st.expander("Updated Data Preview"):
                st.dataframe(cleaner.df.head())
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # --- Duplicate Removal ---
    st.sidebar.markdown("### Remove Duplicates")
    if st.sidebar.button("Remove All Duplicates",key='remove duplicates'):
        try:
            before = len(st.session_state.cleaner.df)
            st.session_state.cleaner.remove_duplicates()
            after = len(st.session_state.cleaner.df)
            removed = before - after
            st.success(f"{removed} duplicate rows removed successfully!")
        except Exception as e:
            st.error(f"Error while removing duplicates: {str(e)}")

    # --- Outlier Removal ---
    st.sidebar.markdown("### Handle Outliers")

    # Get numeric columns only
    numeric_cols = get_numeric_columns(cleaner.df)

    if not numeric_cols:
        st.sidebar.warning("No numeric columns available for outlier handling.")
    else:
        selected_outlier_col = st.sidebar.selectbox("Select numeric column", numeric_cols, key='select_numeric_for_duplicate')
        selected_method = st.sidebar.selectbox("Select outlier handling method", ['IQR', 'z_score'], key='outlier_handling')

        if st.sidebar.button("Apply Outlier Removal",key='remove outliers'):
            try:
                before = len(st.session_state.cleaner.df)
                st.session_state.cleaner.remove_outliers(selected_outlier_col, selected_method)
                after = len(st.session_state.cleaner.df)
                removed = before - after
                st.success(
                    f"Outliers removed from '{selected_outlier_col}' using {selected_method} method ({removed} rows affected).")
            except Exception as e:
                st.error(f"Error during outlier removal: {str(e)}")

        # --- Encoding Section ---
        st.sidebar.markdown("### Encode Categoricals")

        categorical_columns = get_categorical_columns(st.session_state.cleaner.df)

        if not categorical_columns:
            st.sidebar.info("No categorical columns available for encoding.")
        else:
            selected_encoding_col = st.sidebar.selectbox(
                "Select column to encode",
                categorical_columns,
                key="encode_col_select"
            )

            selected_encoding_method = st.sidebar.selectbox(
                "Select encoding method",
                ["OneHot", "LabelEncoding"],
                key="encode_method_select"
            )

            if st.sidebar.button("Apply Encoding", key="apply_encoding_btn"):
                try:
                    before_cols = len(st.session_state.cleaner.df.columns)
                    st.session_state.cleaner.encode_categoricals(selected_encoding_col, selected_encoding_method)
                    after_cols = len(st.session_state.cleaner.df.columns)
                    added_cols = after_cols - before_cols

                    if selected_encoding_method.lower() == 'labelencoding':
                        st.success(
                            f"{selected_encoding_col} encoded successfully using Label Encoding (no new columns added).")
                    else:
                        st.success(
                            f"{selected_encoding_col} encoded successfully using One-Hot Encoding — {added_cols} new columns added.")
                    with st.expander("Preview Encoded Data (sample 5 rows)"):
                        st.dataframe(st.session_state.cleaner.df.sample(5))
                except Exception as e:
                    st.error(f"Error while encoding '{selected_encoding_col}': {str(e)}")

        # --- Scaling Section ---
        st.sidebar.markdown("### Scale Numeric Features")

        numeric_columns = get_numeric_columns(st.session_state.cleaner.df)

        if not numeric_columns:
            st.sidebar.info("No numeric columns available for scaling.")
        else:
            selected_numeric_cols = st.sidebar.multiselect(
                "Select columns to scale",
                numeric_columns,
                key="scale_cols_multiselect"
            )

            selected_scaler = st.sidebar.selectbox(
                "Select scaling method",
                ["StandardScaler", "MinMaxScaler", "RobustScaler"],
                key="scaling_method_select"
            )

            if st.sidebar.button("Apply Scaling", key="apply_scaling_btn"):
                try:
                    if selected_numeric_cols:
                        st.session_state.cleaner.scale_features(selected_numeric_cols, selected_scaler)
                        st.success(f"Columns {selected_numeric_cols} scaled successfully using {selected_scaler}.")

                        with st.expander("Preview Scaled Data (sample 5 rows)"):
                            st.dataframe(st.session_state.cleaner.df.sample(5))
                    else:
                        st.warning("Please select at least one numeric column to scale.")
                except Exception as e:
                    st.error(f"Error while scaling: {str(e)}")


# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small>Data Analyzer v1.0<br>Built by Zeeshan Akram</small>",
    unsafe_allow_html=True
)

