# core/utils.py
import pandas as pd
import os

def load_file(file_path):
    """
    Load a CSV or Excel file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the file (must end with .csv, .xls, or .xlsx).

    Returns
    -------
    pd.DataFrame or None
        Returns the loaded DataFrame, or None if an error occurred.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None

    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            print("Error: Unsupported file type. Please provide CSV or Excel file.")
            return None
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        return None
    except Exception as e:
        print(f"Error loading file '{file_path}': {e}")
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