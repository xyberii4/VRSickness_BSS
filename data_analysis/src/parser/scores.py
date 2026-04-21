from pathlib import Path
import pandas as pd
from docx import Document


class ScoreParser:
    def __init__(self, metadata_path: str | Path):
        self.metadata_df = pd.read_excel(metadata_path).set_index("ID")

    def get_vimssq(self, p_id: int):
        return int(self.metadata_df.loc[p_id, "VIMSSQ"])

    def parse_session_csv(self, csv_path: str | Path):
        """returns event ts and fms scores"""
        df = pd.read_csv(csv_path)

        events = dict(zip(df["Event"], df["Timestamp"]))

        fms_rows = df[df["Event"] == "FMS_Score_Entered"]
        fms_vals = fms_rows["Value"].astype(int).tolist()
        fms_scores = dict(enumerate(fms_vals, start=1))

        return events, fms_scores

    def get_tolerability_score(self, fp: str | Path, weight_val: float = 0.5):
        doc = Document(fp)
        table = doc.tables[0]

        score = 0

        for row in table.rows[1:]:
            cells = row.cells

            intensity_str = cells[1].text.strip()
            try:
                intensity = float(intensity_str)
            except ValueError:
                print(
                    f"could not convert tolerability intensity: found {intensity_str}"
                )
                intensity = 0.0

            weight_str = cells[2].text.strip().lower()
            weight = (1 if "yes" in weight_str else 0) * weight_val

            score += intensity + (intensity * weight)

        return score

    def get_sickness_scores(self, fp: str | Path):
        """get ssq, vrsq and csq scores"""
        xls = pd.ExcelFile(fp)
        sheet_names = xls.sheet_names

        scores = {}

        for sheet, tp in [(0, "Pre"), (1, "Post")]:
            df = pd.read_excel(fp, sheet_name=sheet_names[sheet], header=None)

            scores[tp] = {
                "SSQ_Total": float(df.iloc[25, 4]),
                "SSQ_Nausea": float(df.iloc[22, 4]),
                "SSQ_Oculomotor": float(df.iloc[23, 4]),
                "SSQ_Disorientation": float(df.iloc[24, 4]),
                "VRSQ_Total": float(df.iloc[18, 11]),
                "VRSQ_Disorientation": float(df.iloc[17, 11]),
                "VRSQ_Oculomotor": float(df.iloc[16, 11]),
                "CSQ_Dizziness": float(df.iloc[13, 16]),
                "CSQ_Difficulty_Focusing": float(df.iloc[13, 16]),
            }

        return scores
