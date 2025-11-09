import pandas as pd
from core.analyzer import DataAnalyzer
# simple DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [2, 4, 6, 8, 10],
    'C': [5, 4, 3, 2, 1]
})

analyzer = DataAnalyzer(df)
print(analyzer.generate_report())
