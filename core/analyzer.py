import pandas as pd
from core.utils import get_numeric_columns, get_categorical_columns
from core.cleaner import BaseValidator

class DataAnalyzer(BaseValidator):
    def __init__(self, df):
        self.df = df

    def basic_info(self):
        """
        Returns a summary of the DataFrame including shape, column dtypes, and memory usage in MB.

        Returns:
            dict: {"shape": tuple, "dtypes": dict, "memory": str}
        """
        self._validate_dataframe()

        return {
            "shape": self.df.shape,
            "dtypes": self.df.dtypes.apply(str).to_dict(),
            "memory": f"{self.df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB"
        }

    def missing_summary(self):
        """
        Returns a summary of missing values in each column.

        For each column, provides:
        - missing_count: number of missing/null values
        - missing_percent: percentage of missing values (0-100)

        Returns:
            pd.DataFrame: columns=["missing_count", "missing_percent"]
        """
        self._validate_dataframe()

        total_count = self.df.isnull().sum()
        percent_count = (total_count / self.df.shape[0] * 100).round(2)

        return pd.DataFrame({
            "missing_count": total_count,
            "missing_percent": percent_count
        })

    def duplicate_summary(self):
        """
        Returns a count of duplicate rows in the DataFrame.

        Returns:
            dict: {'duplicate_rows': int}
        """
        self._validate_dataframe()
        duplicate_count = int(self.df.duplicated().sum())
        return {'duplicate_rows': duplicate_count}

    def numeric_summary(self):
        """
        Returns summary statistics for numeric columns:
        mean, median, std, skew, and kurtosis.

        Returns:
            pd.DataFrame: summary stats for each numeric column.
        """
        self._validate_dataframe()

        numeric_cols = get_numeric_columns(self.df)
        if not numeric_cols:
            raise ValueError("No numeric columns found in the DataFrame.")

        numeric_data = self.df[numeric_cols]

        stats = {
            'mean': numeric_data.mean(),
            'median': numeric_data.median(),
            'std': numeric_data.std(),
            'skew': numeric_data.skew(),
            'kurtosis': numeric_data.kurt()
        }

        return pd.DataFrame(stats).T

    def categorical_summary(self):
        """
        Returns summary statistics for categorical columns:
        - nunique: number of unique values
        - mode: most frequent value
        - freq: frequency of the most frequent value
        """
        self._validate_dataframe()

        categorical_cols = get_categorical_columns(self.df)
        if not categorical_cols:
            raise ValueError("No categorical columns found in the DataFrame.")

        categorical_data = self.df[categorical_cols]
        summary = {'nunique': [], 'mode': [], 'freq': []}

        for col in categorical_data.columns:
            nunique = categorical_data[col].nunique(dropna=True)
            mode_values = categorical_data[col].mode(dropna=True)
            top_value = mode_values.iloc[0] if not mode_values.empty else None
            freq = categorical_data[col].value_counts(dropna=True).iloc[0] if categorical_data[col].count() > 0 else 0

            summary['nunique'].append(nunique)
            summary['mode'].append(top_value)
            summary['freq'].append(freq)

        return pd.DataFrame(summary, index=categorical_data.columns)

    def correlation_matrix(self):
        """
        Computes and returns the correlation matrix for numeric columns only.

        Returns:
            pd.DataFrame: Correlation matrix of numeric features.
        """
        self._validate_dataframe()

        numeric_cols = get_numeric_columns(self.df)
        if not numeric_cols:
            raise ValueError("No numeric columns found to compute correlation matrix.")

        return self.df[numeric_cols].corr(numeric_only=True)

    def generate_report(self):
        """
        Generates a comprehensive analysis report of the DataFrame
        by combining outputs from all analysis methods.

        Returns:
            dict: complete report with all summaries (safe even if some fail)
        """
        self._validate_dataframe()

        report = {}
        methods = {
            "basic_info": self.basic_info,
            "missing_summary": lambda: self.missing_summary().to_dict(orient='index'),
            "duplicate_summary": self.duplicate_summary,
            "numeric_summary": lambda: self.numeric_summary().to_dict(),
            "categorical_summary": lambda: self.categorical_summary().to_dict(orient='index'),
            "correlation_matrix": lambda: self.correlation_matrix().to_dict()
        }

        for name, func in methods.items():
            try:
                report[name] = func()
            except Exception as e:
                report[name] = {"error": str(e)}

        return report