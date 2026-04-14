import numpy as np
from scipy.stats import wilcoxon, friedmanchisquare, spearmanr


class StatisticalAnalyzer:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def cohens_d_paired(a, b):
        """get cohen's d"""
        diff = a - b
        std_diff = np.std(diff, ddof=1)

        return np.mean(diff) / std_diff

    @staticmethod
    def run_wilcoxon(a, b):
        """wilcoxon signed-rank test"""
        stat, p = wilcoxon(a, b)
        return stat, p

    def run_spearman_correlation(self, var1="ITC_Norm", var2="FMS"):
        """
        spearman rank correlation between two variables
        returns rho-statistic and p-value
        """
        rho, p_val = spearmanr(self.df[var1], self.df[var2])

        print(f"\n--- Spearman Correlation: {var1} vs {var2} ---")
        print(f"rho = {rho:.4f}, p-value = {p_val:.4f} (n={len(self.df)})")

        return rho, p_val

    def get_delta(self, metric):
        """
        get growth for metric (run 3 - run 1)
        """
        df_runs = self.df[self.df["Run_Number"].isin([1, 3])].copy()

        df_delta = df_runs.pivot(
            index=["Participant_ID", "Session_Type"],
            columns="Run_Number",
            values=metric,
        ).reset_index()

        df_delta = df_delta.rename(columns={1: "Run_1", 3: "Run_3"})
        df_delta[f"{metric}_Growth"] = df_delta["Run_3"] - df_delta["Run_1"]
        df_delta = df_delta.dropna(subset=[f"{metric}_Growth"])

        df_paired = df_delta.pivot(
            index="Participant_ID", columns="Session_Type", values=f"{metric}_Growth"
        ).reset_index()

        return df_paired

    def get_ssq_shift(self):
        """Calculates the Post - Pre SSQ shift."""
        df_ssq = (
            self.df[["Participant_ID", "Session_Type", "Pre_SSQ", "Post_SSQ"]]
            .drop_duplicates()
            .copy()
        )
        df_ssq["SSQ_Shift"] = df_ssq["Post_SSQ"] - df_ssq["Pre_SSQ"]
        df_ssq = df_ssq.dropna(subset=["SSQ_Shift"])

        return df_ssq.pivot(
            index="Participant_ID", columns="Session_Type", values="SSQ_Shift"
        ).reset_index()

    def run_test(self, title, df_paired):
        """
        omnibus friedman and pairwise wilcoxon tests for real vs. sham and real vs. active.
        returns test statistics, p-values, and effect sizes
        """
        print(f"\n--- {title} ---")

        results = {"friedman": None, "real_vs_sham": None, "real_vs_active": None}

        # omnibus friedman
        cols = [c for c in ["Real", "Active", "Sham"] if c in df_paired.columns]
        df_omni = df_paired.dropna(subset=cols)

        if len(cols) == 3 and len(df_omni) > 2:
            fstat, fp = friedmanchisquare(
                df_omni["Real"], df_omni["Active"], df_omni["Sham"]
            )
            print(
                f"[Omnibus Friedman] (n={len(df_omni)}) -> chi2: {fstat:.4f}, p: {fp:.4f}"
            )

            results["friedman"] = {"chi2": fstat, "p_value": fp, "n": len(df_omni)}

        # real vs. sham
        if "Real" in df_paired.columns and "Sham" in df_paired.columns:
            df_rs = df_paired.dropna(subset=["Real", "Sham"])
            stat, p = self.run_wilcoxon(df_rs["Real"].values, df_rs["Sham"].values)
            d = self.cohens_d_paired(df_rs["Real"].values, df_rs["Sham"].values)

            print(
                f"[Real vs Sham] (n={len(df_rs)}) -> W: {stat:.4f}, p: {p:.4f}, d: {d:.4f}"
            )

            results["real_vs_sham"] = {
                "W_stat": stat,
                "p_value": p,
                "cohens_d": d,
                "n": len(df_rs),
            }

        # real vs. active
        if "Real" in df_paired.columns and "Active" in df_paired.columns:
            df_ra = df_paired.dropna(subset=["Real", "Active"])
            stat, p = self.run_wilcoxon(df_ra["Real"].values, df_ra["Active"].values)
            d = self.cohens_d_paired(df_ra["Real"].values, df_ra["Active"].values)

            print(
                f"[Real vs Active] (n={len(df_ra)}) -> W: {stat:.4f}, p: {p:.4f}, d: {d:.4f}"
            )

            results["real_vs_active"] = {
                "W_stat": stat,
                "p_value": p,
                "cohens_d": d,
                "n": len(df_ra),
            }

        return results
