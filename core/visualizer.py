import matplotlib.pyplot as plt
import seaborn as sns
import os

class DataVisualizer:
    def __init__(self, df):
        self.df = df

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

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        plt.figure(figsize=(8, 5))
        sns.heatmap(self.df.isnull(), cbar=False, yticklabels=False)
        plt.title("Missing Values Heatmap")
        plt.tight_layout()
        plt.savefig(file_path, dpi=300)
        plt.close()

    def plot_correlation_heatmap(self, file_path):
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        plt.figure(figsize=(8, 5))
        sns.heatmap(self.df.corr(numeric_only=True), annot=True)
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(file_path, dpi=300)
        plt.close()
