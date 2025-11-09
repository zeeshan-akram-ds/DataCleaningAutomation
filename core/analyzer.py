import pandas as pd
from core.utils import get_numeric_columns, get_categorical_columns

class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def basic_info(self):
        """
        Returns a summary of the DataFrame including shape, column dtypes, and memory usage in MB.

        Returns:
            dict: {"shape": tuple, "dtypes": dict, "memory": str}
        """
        return {
            "shape": self.df.shape,
            "dtypes": self.df.dtypes.apply(lambda x: str(x)).to_dict(),
            "memory": f"{self.df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB"
        }

    def missing_summary(self):
        """
        Returns a summary of missing values in each column.

        For each column, provides:
        - missing_count: number of missing/null values
        - missing_percent: fraction of missing values (0-1)

        Returns:
            pd.DataFrame: columns=["missing_count", "missing_percent"]
        """
        total_count = self.df.isnull().sum()
        percent_count = (total_count / self.df.shape[0] * 100).round(2)

        return pd.DataFrame({"missing_count": total_count, "missing_percent": percent_count})

    def duplicate_summary(self):
        duplicate_count = int(self.df.duplicated().sum())

        return {'duplicate_rows': duplicate_count}

    def numeric_summary(self):
        """
        Returns summary statistics for numeric columns:
        mean, median, std, skew, and kurtosis.
        """
        numeric_cols = get_numeric_columns(self.df)
        numeric_data = self.df[numeric_cols]

        # compute statistics
        stats = {
            'mean': numeric_data.mean(),
            'median': numeric_data.median(),
            'std': numeric_data.std(),
            'skew': numeric_data.skew(),
            'kurtosis': numeric_data.kurt()
        }

        # convert to DataFrame
        result = pd.DataFrame(stats)
        return result.T  # transpose so stats are rows, columns are numeric columns

    def categorical_summary(self):
        """
        Returns summary statistics for categorical columns:
        - nunique: number of unique values
        - mode: most frequent value
        - freq: frequency of the most frequent value
        """
        # select categorical columns
        categorical_cols = get_categorical_columns(self.df)
        categorical_data = self.df[categorical_cols]

        # prepare summary dicts
        summary = {'nunique': [], 'mode': [], 'freq': []}

        for col in categorical_data.columns:
            summary['nunique'].append(categorical_data[col].nunique())

            # mode may return multiple values; take the first
            top_value = categorical_data[col].mode().iloc[0] if not categorical_data[col].mode().empty else None
            summary['mode'].append(top_value)

            # frequency of the top value
            freq = categorical_data[col].value_counts().iloc[0] if not categorical_data[col].empty else 0
            summary['freq'].append(freq)

        # convert to DataFrame
        result = pd.DataFrame(summary, index=categorical_data.columns)
        return result

    def correlation_matrix(self):
        return self.df.corr(numeric_only=True)

    def generate_report(self):
        """
        Generates a comprehensive analysis report of the DataFrame
        by combining outputs from all analysis methods.

        Returns:
            dict: complete report with all summaries
        """
        report = {
            "basic_info": self.basic_info(),
            "missing_summary": self.missing_summary().to_dict(orient='index'),  # convert DataFrame to dict
            "duplicate_summary": self.duplicate_summary(),
            "numeric_summary": self.numeric_summary().to_dict(),  # numeric summary as dict of columns
            "categorical_summary": self.categorical_summary().to_dict(orient='index'),  # categorical summary as dict
            "correlation_matrix": self.correlation_matrix().to_dict()  # correlation as nested dict
        }

        return report