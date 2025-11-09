from core.analyzer import DataAnalyzer
from core.recommender import RecommendationEngine
from core.visualizer import DataVisualizer
from core.cleaner import DataCleaner
from core.utils import load_file

df = load_file('data/titanicdataset.csv')
if df is None:
    raise TypeError("Error")
da = DataAnalyzer(df)
report = da.generate_report()
re = RecommendationEngine(report)
# print(re.generate_suggestions())
dc = DataCleaner(df)
#
dc.handle_missing(col_name='Age', strategy='median', fill_value=None).remove_duplicates()
#
dv = DataVisualizer(df)
dv.plot_correlation_heatmap(file_path='outputs/plots/correlation.png')
dc.save_cleaned('outputs/cleaned_data.csv')