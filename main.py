from core.visualizer import DataVisualizer
import pandas as pd

# --- Synthetic numeric dataset ---
data = {
    'Age': [22, 25, 47, 52, 46, 56, 23, 43, 36, 29],
    'Salary': [25000, 30000, 47000, 52000, 48000, 58000, 26000, 49000, 41000, 31000],
    'Experience': [1, 3, 10, 15, 12, 20, 2, 14, 9, 4]
}

df = pd.DataFrame(data)

# --- Initialize your visualizer ---
viz = DataVisualizer(df)

# --- Test pairplot_numeric ---
viz.pairplot_numeric(file_path="outputs/pairplot_numeric.png")
print("Pairplot saved successfully at outputs/pairplot_numeric.png")