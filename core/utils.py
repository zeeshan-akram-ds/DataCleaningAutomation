# core/utils.py
import pandas as pd
import os
import json
from io import BytesIO, StringIO

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
