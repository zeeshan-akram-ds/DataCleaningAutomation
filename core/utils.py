# core/utils.py
import pandas as pd
import os
import json
from io import BytesIO, StringIO
import streamlit as st
import re

def load_file(file_input):
    """
    Load a CSV or Excel file into a pandas DataFrame.

    Parameters
    ----------
    file_input : str or file-like
        File path (str) or file-like object (from Streamlit).

    Returns
    -------
    pd.DataFrame or None
        Loaded DataFrame, or None if an error occurred.
    """
    try:
        if isinstance(file_input, str):
            if not os.path.exists(file_input):
                print(f"Error: File '{file_input}' does not exist.")
                return None
            if file_input.endswith('.csv'):
                return pd.read_csv(file_input)
            elif file_input.endswith(('.xls', '.xlsx')):
                return pd.read_excel(file_input)
            else:
                print("Error: Unsupported file type. Please provide CSV or Excel file.")
                return None
        else:
            # file-like object
            if hasattr(file_input, "name") and file_input.name.endswith('.csv'):
                return pd.read_csv(file_input)
            else:
                return pd.read_excel(file_input)

    except pd.errors.EmptyDataError:
        print("Error: File is empty.")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def get_numeric_columns(df):
    """
    Return a list of numeric column names from the DataFrame.
    """
    return df.select_dtypes(include='number').columns.tolist()

def get_categorical_columns(df):
    """
    Return a list of categorical column names (object or category) from the DataFrame.
    """
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def save_json_report(report_dict, file_path):
    """
    Save a Python dictionary as a JSON file.

    Parameters
    ----------
    report_dict : dict
        The report dictionary to save.
    file_path : str
        Path to the JSON file to create.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(report_dict, f, indent=4)
        print(f"Report saved successfully at {file_path}")

    except (OSError, IOError) as e:
        print(f"Error saving JSON file: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


def display_report(report: dict):
    """
    Displays a data analysis report in Streamlit in a clear, structured, and adaptive way.
    Works with any report dictionary structure and presents data neatly.
    """

    # One main expander for the entire report
    with st.expander("Full Data Analysis Report", expanded=False):

        # Iterate through each main section (like basic_info, missing_summary, etc.)
        for section, content in report.items():
            section_title = section.replace('_', ' ').title()  # e.g., "basic_info" → "Basic Info"

            # One expander for each main section
            with st.expander(section_title, expanded=False):

                # --- If the section is a dictionary (most of them are)
                if isinstance(content, dict):

                    # Special handling for known sections:
                    # 1. BASIC INFO section
                    if section == "basic_info":
                        st.subheader("Basic Information")

                        # If 'dtypes' key is present → convert it to DataFrame for nice table display
                        if "dtypes" in content:
                            dtype_df = pd.DataFrame(
                                list(content["dtypes"].items()), columns=["Column", "Data Type"]
                            )
                            st.write(f"**Shape:** {content.get('shape', 'N/A')}")
                            st.write(f"**Memory Usage:** {content.get('memory', 'N/A')}")
                            st.dataframe(dtype_df)
                        else:
                            # If no special keys, just print the dictionary directly
                            st.write(content)

                    # 2. SECTIONS like missing_summary, numeric_summary, etc.
                    elif section in [
                        "missing_summary",
                        "numeric_summary",
                        "categorical_summary",
                        "correlation_matrix",
                    ]:
                        df = pd.DataFrame(content).T  # Transpose so columns become rows
                        st.dataframe(df)

                    # 3. DUPLICATE SUMMARY
                    elif section == "duplicate_summary":
                        dup_count = content.get("duplicate_rows", 0)
                        if dup_count > 0:
                            st.error(f"{dup_count} duplicate rows found.")
                        else:
                            st.success("No duplicate rows found.")

                    # 4. FALLBACK: For any future sections not listed above
                    else:
                        try:
                            st.dataframe(pd.DataFrame(content).T)
                        except Exception:
                            st.write(content)

                # --- If the section content is a list or tuple (like shape info)
                elif isinstance(content, (list, tuple)):
                    st.write(pd.DataFrame(content))

                # --- If it’s just a number, string, or single value
                else:
                    st.write(content)


def display_recommendations(recommendations):
    """
    Display model/data cleaning recommendations in a structured, readable format.

    Parameters:
        recommendations (list): A list of recommendation strings.
    """

    if not recommendations:
        st.info("No recommendations available.")
        return

    # --- Categorize recommendations by keyword ---
    categories = {
        "Missing Values": [],
        "High Cardinality": [],
        "Skewness": [],
        "Kurtosis": [],
        "Other": []
    }

    for rec in recommendations:
        if re.search(r"missing values", rec, re.IGNORECASE):
            categories["Missing Values"].append(rec)
        elif re.search(r"cardinality", rec, re.IGNORECASE):
            categories["High Cardinality"].append(rec)
        elif re.search(r"skew", rec, re.IGNORECASE):
            categories["Skewness"].append(rec)
        elif re.search(r"kurtosis", rec, re.IGNORECASE):
            categories["Kurtosis"].append(rec)
        else:
            categories["Other"].append(rec)

    # --- Display section title ---
    st.markdown("### Recommendations Summary")

    # --- Display each category neatly ---
    for category, items in categories.items():
        if not items:
            continue

        with st.expander(category, expanded=False):
            for rec in items:
                # Apply mild markdown formatting
                if "high" in rec.lower():
                    st.markdown(
                        f"<div style='background-color:#ffe5e5;padding:8px;border-radius:6px;margin-bottom:4px'>{rec}</div>",
                        unsafe_allow_html=True)
                elif "moderate" in rec.lower():
                    st.markdown(
                        f"<div style='background-color:#fff4e6;padding:8px;border-radius:6px;margin-bottom:4px'>{rec}</div>",
                        unsafe_allow_html=True)
                elif "minor" in rec.lower() or "no action" in rec.lower():
                    st.markdown(
                        f"<div style='background-color:#eafbea;padding:8px;border-radius:6px;margin-bottom:4px'>{rec}</div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='background-color:#f0f0f0;padding:8px;border-radius:6px;margin-bottom:4px'>{rec}</div>",
                        unsafe_allow_html=True)