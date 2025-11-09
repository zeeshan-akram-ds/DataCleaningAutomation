import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler

class DataCleaner:
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
        valid_strategies = ['mean', 'median', 'mode', 'constant', 'drop']
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy. Choose from {valid_strategies}")

        if col_name not in self.df.columns:
            raise KeyError(f"Column '{col_name}' not found in DataFrame")

        if strategy == 'mean':
            self.df[col_name] = self.df[col_name].fillna(self.df[col_name].mean())

        elif strategy == 'median':
            self.df[col_name] = self.df[col_name].fillna(self.df[col_name].median())

        elif strategy == 'mode':
            mode_value = self.df[col_name].mode(dropna=True)
            if not mode_value.empty:
                self.df[col_name] = self.df[col_name].fillna(mode_value[0])

        elif strategy == 'constant':
            if fill_value is None:
                raise ValueError("You must provide a 'fill_value' when using the 'constant' strategy.")
            self.df[col_name] = self.df[col_name].fillna(fill_value)

        elif strategy == 'drop':
            self.df.dropna(subset=[col_name], inplace=True)

        return self

    def remove_duplicates(self, subset=None, keep='first'):
        self.df.drop_duplicates(subset = subset, keep = keep,inplace=True)
        return self

    def remove_outliers(self, col_name, method='IQR'):
        valid_methods = ['IQR', 'z_score']

        if col_name not in self.df.columns:
            raise KeyError(f"Column '{col_name}' not found in DataFrame")

        if method not in valid_methods:
            raise ValueError(f"Choose from {valid_methods}")

        if method == "IQR":
            q1 = self.df[col_name].quantile(0.25)
            q3 = self.df[col_name].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            self.df = self.df[(self.df[col_name] >= lower_bound) & (self.df[col_name] <= upper_bound)]

        elif method == "z_score":
            z_scores = (self.df[col_name] - self.df[col_name].mean()) / self.df[col_name].std()
            abs_z = np.abs(z_scores)
            self.df = self.df[abs_z < 3]  # keep only rows within 3 std deviations

        return self

    def encode_categoricals(self, col, method='LabelEncoder'):
        valid_methods = ['LabelEncoder', 'OneHot']
        if col not in self.df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame")

        if method not in valid_methods:
            raise ValueError(f"Choose from {valid_methods}")

        if method == 'OneHot':
            # One-hot encode (drop_first avoids dummy trap)
            encoded = pd.get_dummies(self.df[col], prefix=col, drop_first=True, dtype=int)
            self.df = pd.concat([self.df.drop(columns=[col]), encoded], axis=1)

        else:  # LabelEncoder
            le = LabelEncoder()
            # Handle NaN safely (LabelEncoder doesn’t accept NaNs)
            non_null_mask = self.df[col].notnull()
            self.df.loc[non_null_mask, col] = le.fit_transform(self.df.loc[non_null_mask, col])

        return self

    def scale_features(self, cols, method='StandardScaler'):
        valid_methods = ['StandardScaler', 'MinMaxScaler', 'RobustScaler']

        # Handle single column or list of columns
        if isinstance(cols, str):
            cols = [cols]

        for col in cols:
            if col not in self.df.columns:
                raise KeyError(f"Column '{col}' not found in DataFrame")

        if method not in valid_methods:
            raise ValueError(f"Choose from {valid_methods}")

        # Select scaler
        if method == 'StandardScaler':
            scaler = StandardScaler()
        elif method == 'MinMaxScaler':
            scaler = MinMaxScaler()
        else:
            scaler = RobustScaler()

        # Apply scaling
        self.df[cols] = scaler.fit_transform(self.df[cols])

        return self

    def drop_constant_columns(self):
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
        self.df.to_csv(file_path, index=False)
        print(f"Cleaned dataset successfully saved to: {file_path}")

    