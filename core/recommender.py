

class RecommendationEngine:
    def __init__(self, report_dict):
        self.report_dict = report_dict

    def generate_suggestions(self):
        """
        Generate data-cleaning suggestions based on the report dictionary.

        Returns
        -------
        suggestions : list
            A list of textual recommendations for handling data issues.
        """

        if not isinstance(self.report_dict, dict):
            raise ValueError("Input 'report_dict' must be a dictionary.")

        required_keys = ['missing_summary', 'duplicate_summary', 'categorical_summary', 'numeric_summary']
        for key in required_keys:
            if key not in self.report_dict:
                raise ValueError(f"Missing expected key '{key}' in report dictionary.")

        suggestions = []

        missing_summary = self.report_dict.get('missing_summary', {})
        duplicate_count = self.report_dict.get('duplicate_summary', {}).get('duplicate_rows', 0)
        categorical_summary = self.report_dict.get('categorical_summary', {})
        numeric_summary = self.report_dict.get('numeric_summary', {})

        for col, stats in missing_summary.items():
            missing_percent = stats.get('missing_percent', 0)

            if 0 < missing_percent <= 5:
                suggestions.append(
                    f"Column '{col}' has minor missing values ({missing_percent:.1f}%). Consider imputing with mean/median/mode.")
            elif 5 < missing_percent <= 30:
                suggestions.append(
                    f"Column '{col}' has moderate missing values ({missing_percent:.1f}%). Consider advanced imputation (e.g., KNN, regression).")
            elif missing_percent > 30:
                suggestions.append(
                    f"Column '{col}' has high missing values ({missing_percent:.1f}%). Consider dropping the column or using domain-specific imputation.")
            else:
                suggestions.append(f"Column '{col}' has no missing values — no action needed.")

        if duplicate_count > 0:
            suggestions.append(
                f"Data contains {duplicate_count} duplicate rows. Consider removing them."
            )
        for col, stats in categorical_summary.items():
            nunique = stats.get('nunique', 0)

            if nunique > 50:
                suggestions.append(
                    f"Column '{col}' has high cardinality ({nunique} unique values). Avoid OneHot encoding."
                )
            elif nunique == 1:
                suggestions.append(
                    f"Column '{col}' has only 1 unique value. Consider dropping it."
                )

        for col, stats in numeric_summary.items():
            skew = abs(stats.get('skew', 0))
            kurt = stats.get('kurtosis', 0)

            if skew > 3:
                suggestions.append(
                    f"Column '{col}' is highly skewed (Skew: {skew:.2f}). Consider Box-Cox transformation."
                )
            elif skew > 1:
                suggestions.append(
                    f"Column '{col}' is moderately skewed (Skew: {skew:.2f}). Consider log or square root transformation."
                )

            if kurt > 3:
                suggestions.append(
                    f"Column '{col}' has high kurtosis (Kurtosis: {kurt:.2f}). Consider handling potential outliers."
                )
        return suggestions