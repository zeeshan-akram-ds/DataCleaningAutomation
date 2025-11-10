import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from core.cleaner import BaseValidator

class DataVisualizer(BaseValidator):
    def __init__(self, df):
        self.df = df

    def helper_plot(
            self,
            plot_type,
            title,
            file_path,
            diag='hist',
            data=None,
            col=None,
            cbar=True,
            yticklabels=True,
            annot=False,
            color=None
    ):
        """
        Generic helper to generate and save different Seaborn plots.

        Parameters
        ----------
        plot_type : str
            Type of plot to generate ('heatmap', 'countplot', 'boxplot', 'pairplot').
        title : str
            Title for the plot.
        file_path : str
            Path to save the generated plot image.
        diag : str, optional
            Type of diagonal plot for pairplot ('hist' or 'kde'), by default 'hist'.
        data : pd.DataFrame, optional
            The dataset to visualize (required for 'heatmap' and 'pairplot').
        col : str, optional
            Column name (required for 'countplot' or 'boxplot').
        cbar, yticklabels, annot, color : various, optional
            Plot customization parameters.
        """

        # VALIDATIONS
        self._validate_dataframe()
        self._validate_plot_type(plot_type, ['heatmap', 'countplot', 'boxplot', 'pairplot'])

        # Directory check
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # PLOT LOGIC
        plt.figure(figsize=(8, 5))

        if plot_type == 'heatmap':
            if data is None or data.empty:
                raise ValueError("Data must not be empty for a heatmap.")
            self._validate_numeric_dataframe(data)
            sns.heatmap(data, annot=annot, cbar=cbar, yticklabels=yticklabels)

        elif plot_type == 'countplot':
            self._validate_column_exists(col)
            self._validate_categorical_column(col)
            sns.countplot(x=self.df[col], color=color)

        elif plot_type == 'boxplot':
            self._validate_column_exists(col)
            self._validate_numeric_column(col)
            sns.boxplot(x=self.df[col], color=color)

        else:  # pairplot
            if data is None or data.empty:
                raise ValueError("Data must not be empty for a pairplot.")
            self._validate_numeric_dataframe(data)
            self._validate_diag_kind(diag)
            sns.pairplot(data, diag_kind=diag)

        # finally
        plt.title(title)
        plt.tight_layout()
        plt.savefig(file_path, dpi=300)
        plt.close()

    def plot_missing_heatmap(self, file_path):
        """
        Plot and save a heatmap showing missing values in the dataset.

        Parameters
        ----------
        file_path : str
            Path (including filename) where the heatmap image will be saved.

        Returns
        -------
        None
        """

        self.helper_plot('heatmap', "Missing Values Heatmap", file_path, data=self.df.isnull(), cbar=False, yticklabels=False)

    def plot_correlation_heatmap(self, file_path):
        self.helper_plot('heatmap', "Correlation Heatmap", file_path, data=self.df.corr(numeric_only=True), annot=True)

    def plot_value_counts(self, col, file_path):
        self.helper_plot('countplot', f"Value Counts for {col}", file_path, col=col)

    def plot_outliers(self, col, file_path):
        if col not in self.df.select_dtypes(include='number').columns.to_list():
            raise TypeError("column must be of numeric data type.")
        self.helper_plot(
            plot_type='boxplot',
            title=f"Outlier Distribution - {col}",
            file_path=file_path,
            col=col,
            color='skyblue'
        )

    def pairplot_numeric(self, file_path, subset=None):
        if subset is not None:
            missing_cols = [col for col in subset if col not in self.df.columns]
            if missing_cols:
                raise ValueError(f"These columns are not in the DataFrame: {missing_cols}")
            numeric_cols = self.df[subset].select_dtypes(include='number')
        else:
            numeric_cols = self.df.select_dtypes(include='number')

        if numeric_cols.shape[1] < 2:
            raise ValueError("Need at least two numeric columns to create a pairplot.")

        self.helper_plot(
            plot_type='pairplot',
            title="PairPlot of Numeric Columns",
            file_path=file_path,
            data=numeric_cols
        )