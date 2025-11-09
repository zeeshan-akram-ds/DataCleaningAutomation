import matplotlib.pyplot as plt
import seaborn as sns
import os

class DataVisualizer:
    def __init__(self, df):
        self.df = df

    def helper_plot(self, plot_type, title, file_path, data=None, col=None, cbar=True, yticklabels=True, annot=False, color=None):
        """
        Generic helper to generate and save different Seaborn plots.

        Parameters
        ----------
        plot_type : str
            Type of plot to generate ('heatmap', 'countplot' or 'boxplot').
        title : str
            Title for the plot.
        file_path : str
            Path to save the generated plot image.
        data : data
            data for heatmap graph
        col : str, optional
            Column name (required for 'countplot').
        cbar, yticklabels, annot, color : various, optional
            Plot customization parameters.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        allowed_plots = ['heatmap', 'countplot', 'boxplot']
        if plot_type not in allowed_plots:
            raise ValueError(f"Invalid plot type. Choose from {allowed_plots}.")

        plt.figure(figsize=(8, 5))

        if plot_type == 'heatmap':
            if data is None:
                raise ValueError("Data must not empty")
            sns.heatmap(data, annot=annot, cbar=cbar, yticklabels=yticklabels)
        elif plot_type == 'countplot':
            if col is None:
                raise ValueError("Column name must be provided for countplot.")
            sns.countplot(x=self.df[col], color=color)
        elif plot_type == 'boxplot':
            if col is None:
                raise ValueError("Column name must be provided for boxplot.")
            sns.boxplot(x=self.df[col], color=color)

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
        self.helper_plot('heatmap', "Correlation Heatmap", file_path, data=self.df.corr(), annot=True)

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
