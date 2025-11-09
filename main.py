from core.recommender import RecommendationEngine
# Synthetic report dictionary
report_dict = {
    "missing_summary": {
        "Age": {"missing_count": 3, "missing_percent": 3.0},
        "Salary": {"missing_count": 15, "missing_percent": 35.0},
        "Department": {"missing_count": 0, "missing_percent": 0.0}
    },
    "duplicate_summary": {"duplicate_rows": 2},
    "categorical_summary": {
        "Gender": {"nunique": 2, "mode": "Male", "freq": 6},
        "EmployeeID": {"nunique": 120, "mode": "E001", "freq": 1},
        "Country": {"nunique": 1, "mode": "USA", "freq": 10}
    },
    "numeric_summary": {
        "Age": {"mean": 30, "median": 29, "std": 5, "skew": 0.5, "kurtosis": 2},
        "Salary": {"mean": 50000, "median": 48000, "std": 10000, "skew": 4, "kurtosis": 5}
    }
}

# Initialize the engine
engine = RecommendationEngine(report_dict)

# Generate suggestions
suggestions = engine.generate_suggestions()

# Print suggestions
for s in suggestions:
    print(s)
