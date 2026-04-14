from pathlib import Path
import pandas as pd


class ScoreParser:
    def __init__(self, metadata_path: str | Path):
        self.metadata_df = pd.read_excel(metadata_path).set_index("ID")

    def get_vimssq(self, p_id: int):
        return int(self.metadata_df.loc[p_id, "VIMSSQ"])

    def get_ssq(self, p_id: int, session_type: str):
        pre_col = f"SSQ_1_{session_type}"
        post_col = f"SSQ_2_{session_type}"

        pre_ssq = float(self.metadata_df.loc[p_id, pre_col])
        post_ssq = float(self.metadata_df.loc[p_id, post_col])

        return pre_ssq, post_ssq

    def parse_session_csv(self, csv_path: str | Path):
        """returns event ts and fms scores"""
        df = pd.read_csv(csv_path)

        events = dict(zip(df["Event"], df["Timestamp"]))

        fms_rows = df[df["Event"] == "FMS_Score_Entered"]
        fms_vals = fms_rows["Value"].astype(int).tolist()
        fms_scores = dict(enumerate(fms_vals, start=1))

        return events, fms_scores
