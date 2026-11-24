from torch.utils._dtype_abbrs import dtype_abbrs
import os
import pandas as pd 

def generator (dataframe, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    dataframe.to_csv(output_path, index = False)
    if dataframe.empty:
        summary = {
            "total_person_observations": 0,
            "violation_observations": 0,
            "compliant_observations": 0,
            "review_observations": 0
        }
    else:
        summary = {
            "total_person_observations": len(dataframe),
            "violation_observations": int((dataframe["overall_status"] == "Violation").sum()),
            "compliant_observations": int((dataframe["overall_status"] == "Compliant").sum()),
            "review_observations": int((dataframe["overall_status"] == "Needs Review").sum())
        }
    return summary