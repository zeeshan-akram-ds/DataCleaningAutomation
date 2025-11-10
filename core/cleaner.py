import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler


class BaseValidator:
    """Provides reusable validation methods for DataFrame operations."""

    def _validate_dataframe(self):
        """Ensure DataFrame is not empty."""
        if self.df is None or self.df.empty:
            raise ValueError("The DataFrame is empty or not initialized.")

    def _validate_column_exists(self, col_name):
        """Ensure the given column exists in the DataFrame."""
        if col_name not in self.df.columns:
            raise KeyError(f"Column '{col_name}' not found in the DataFrame.")

    def _validate_numeric_column(self, col_name):
        """Ensure the given column is numeric."""
        self._validate_column_exists(col_name)
        if not pd.api.types.is_numeric_dtype(self.df[col_name]):
            raise TypeError(f"Column '{col_name}' must be numeric for this operation.")

    def _validate_categorical_column(self, col_name):
        """Ensure the given column is categorical."""
        self._validate_column_exists(col_name)
        if self.df[col_name].dtype not in ['object', 'category']:
            raise TypeError(f"Column '{col_name}' is not categorical. Operation only applies to categorical columns.")

    def _validate_plot_type(self, plot_type, allowed_types):
        if plot_type not in allowed_types:
            raise ValueError(f"Invalid plot type. Choose from {allowed_types}.")

    def _validate_diag_kind(self, diag_kind):
        if diag_kind not in ['hist', 'kde']:
            raise ValueError("diag_kind must be either 'hist' or 'kde'.")

    def _validate_numeric_dataframe(self, df):
        if not all(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns):
            raise TypeError("All columns in the DataFrame must be numeric for this operation.")


class DataCleaner(BaseValidator):
    def __init__(self, df):
        self.df = df.copy()

    def handle_missing(self, col_name, strategy, fill_value=None):
        """
        Handles missing values in a given column using the specified strategy.

        Parameters:
            col_name (str): Column name to handle.
            strategy (str): One of ['mean', 'median', 'mode', 'constant', 'drop'].
            fill_value (any, optional): Value used if strategy='constant'.

        Returns:
            self: Enables method chaining.
        """

        try:
            self._validate_dataframe()
            self._validate_column_exists(col_name)

            valid_strategies = ['mean', 'median', 'mode', 'constant', 'drop']
            if strategy not in valid_strategies:
                raise ValueError(f"Invalid strategy '{strategy}'. Choose from {valid_strategies}.")

            if strategy in ['mean', 'median']:
                self._validate_numeric_column(col_name)

            if strategy == 'mean':
                self.df[col_name].fillna(self.df[col_name].mean(), inplace=True)
            elif strategy == 'median':
                self.df[col_name].fillna(self.df[col_name].median(), inplace=True)
            elif strategy == 'mode':
                mode_value = self.df[col_name].mode(dropna=True)
                if not mode_value.empty:
                    self.df[col_name].fillna(mode_value[0], inplace=True)
            elif strategy == 'constant':
                if fill_value is None:
                    raise ValueError("You must provide a 'fill_value' when using the 'constant' strategy.")
                self.df[col_name].fillna(fill_value, inplace=True)
            elif strategy == 'drop':
                self.df.dropna(subset=[col_name], inplace=True)

            return self

        except Exception as e:
            raise RuntimeError(f"Error handling missing values for '{col_name}': {str(e)}")

    def remove_duplicates(self, subset=None, keep='first'):
        try:
            self._validate_dataframe()
            self.df.drop_duplicates(subset=subset, keep=keep, inplace=True)
            return self

        except Exception as e:
            raise RuntimeError(f"Error removing duplicates: {str(e)}")

    def remove_outliers(self, col_name, method='IQR'):
        try:
            self._validate_dataframe()
            self._validate_column_exists(col_name)
            self._validate_numeric_column(col_name)

            valid_methods = ['IQR', 'z_score']
            if method not in valid_methods:
                raise ValueError(f"Invalid method '{method}'. Choose from {valid_methods}.")

            if method == 'IQR':
                q1 = self.df[col_name].quantile(0.25)
                q3 = self.df[col_name].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                self.df = self.df[(self.df[col_name] >= lower_bound) & (self.df[col_name] <= upper_bound)]

            elif method == 'z_score':
                z_scores = (self.df[col_name] - self.df[col_name].mean()) / self.df[col_name].std()
                abs_z = np.abs(z_scores)
                self.df = self.df[abs_z < 3]

            return self

        except Exception as e:
            raise RuntimeError(f"Error removing outliers from '{col_name}': {str(e)}")

    def encode_categoricals(self, col, method='LabelEncoder'):
        valid_methods = ['LabelEncoder', 'OneHot']
        self._validate_categorical_column(col)

        if method not in valid_methods:
            raise ValueError(f"Choose from {valid_methods}")

        if method == 'OneHot':
            encoded = pd.get_dummies(self.df[col], prefix=col, drop_first=True, dtype=int)
            self.df = pd.concat([self.df.drop(columns=[col]), encoded], axis=1)
        else:  # LabelEncoder
            le = LabelEncoder()
            non_null_mask = self.df[col].notnull()
            self.df.loc[non_null_mask, col] = le.fit_transform(self.df.loc[non_null_mask, col])

        return self

    def scale_features(self, cols, method='StandardScaler'):
        valid_methods = ['StandardScaler', 'MinMaxScaler', 'RobustScaler']

        # Ensure cols is a list
        if isinstance(cols, str):
            cols = [cols]

        # Validate columns
        for col in cols:
            self._validate_column_exists(col)
            self._validate_numeric_column(col)

        # Validate method
        if method not in valid_methods:
            raise ValueError(f"Choose from {valid_methods}")

        # Select scaler
        scaler = {
            'StandardScaler': StandardScaler(),
            'MinMaxScaler': MinMaxScaler(),
            'RobustScaler': RobustScaler()
        }[method]

        # Apply scaling
        self.df[cols] = scaler.fit_transform(self.df[cols])

        return self

    def drop_constant_columns(self):
        if self.df.empty:
            print("DataFrame is empty. Nothing to drop.")
            return self

        constant_cols = [col for col in self.df.columns if self.df[col].nunique(dropna=False) <= 1]

        if constant_cols:
            self.df.drop(columns=constant_cols, inplace=True)
            print(f"Dropped constant columns: {constant_cols}")
        else:
            print("No constant columns found.")

        return self

    def save_cleaned(self, file_path):
        """
        Save the cleaned DataFrame to a CSV file.

        Parameters
        ----------
        file_path : str
            Path (including filename) where the cleaned DataFrame will be saved.

        Returns
        -------
        None
        """
        if self.df.empty:
            print("Warning: DataFrame is empty. Saving an empty file.")

        try:
            self.df.to_csv(file_path, index=False)
            print(f"Cleaned dataset successfully saved to: {file_path}")
        except Exception as e:
            print(f"Error saving file '{file_path}': {e}")

