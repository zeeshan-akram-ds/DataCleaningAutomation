from core.utils import get_numeric_columns, get_categorical_columns
import pandas as pd

# Synthetic DataFrame
df = pd.DataFrame({
    'Age': [25, 30, 22],
    'Salary': [50000, 60000, 55000],
    'Department': ['HR', 'IT', 'Marketing']
})

print("Numeric columns:", get_numeric_columns(df))
print("Categorical columns:", get_categorical_columns(df))
