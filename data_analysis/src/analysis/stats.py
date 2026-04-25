import numpy as np
import pingouin as pg
from scipy.stats import wilcoxon, friedmanchisquare, spearmanr, permutation_test


class StatisticalAnalyzer:
    def __init__(
        self,
        df,
        subject_col="Participant_ID",
        condition_col="Session_Type",
        time_col="Run_Number",
    ):
        self.df = df
        self.subject_col = subject_col
        self.condition_col = condition_col
        self.time_col = time_col

    @staticmethod
    def _cohens_d_paired(a, b):
        diff = a - b
        std_diff = np.std(diff, ddof=1)
        return np.mean(diff) / std_diff

    @staticmethod
    def _wilcoxon(a, b):
        stat, p = wilcoxon(a, b)
        return stat, p

    def spearman_correlation(self, var1, var2):
        rho, p_val = spearmanr(self.df[var1], self.df[var2])
        print(f"\n--- Spearman Correlation: {var1} vs {var2} ---")
        print(f"rho = {rho:.4f}, p-value = {p_val:.4f} (n={len(self.df)})")
        return rho, p_val

    def partial_spearman(self, var1, var2, covar="Tolerability"):
        clean_df = (
            self.df[[self.subject_col, self.condition_col, var1, var2, covar]]
            .dropna()
            .drop_duplicates()
        )
        n = len(clean_df)

        stats = pg.partial_corr(
            data=clean_df, x=var1, y=var2, covar=covar, method="spearman"
        )

        r_col = next((c for c in stats.columns if c.lower() in ["r", "rho"]), None)
        p_col = next(
            (c for c in stats.columns if "p" in c.lower() and "val" in c.lower()), None
        )

        rho = float(stats[r_col].iloc[0])
        p_val = float(stats[p_col].iloc[0])

        print(f"\n--- Partial Spearman: {var1} vs {var2} (controlling for {covar}) ---")
        print(f"rho = {rho:.4f}, p-value = {p_val:.4f} (n={n})")

        return rho, p_val

    def get_delta(self, metric, start_time=1, end_time=3):
        df_runs = self.df[self.df[self.time_col].isin([start_time, end_time])].copy()

        df_delta = df_runs.pivot(
            index=[self.subject_col, self.condition_col],
            columns=self.time_col,
            values=metric,
        ).reset_index()

        growth_col = f"{metric}_Growth"
        df_delta[growth_col] = df_delta[end_time] - df_delta[start_time]
        df_delta = df_delta.dropna(subset=[growth_col])

        return df_delta.pivot(
            index=self.subject_col, columns=self.condition_col, values=growth_col
        ).reset_index()

    def get_score_shift(self, shift_col):
        df_score = (
            self.df[[self.subject_col, self.condition_col, shift_col]]
            .drop_duplicates()
            .dropna(subset=[shift_col])
        )
        return df_score.pivot(
            index=self.subject_col, columns=self.condition_col, values=shift_col
        ).reset_index()

    def run_test(self, title, df_paired, groups=("Real", "Active", "Sham")):
        """omnibus friedman and pairwise wilcoxon"""
        print(f"\n--- {title} ---")
        results = {"friedman": None, "real_vs_sham": None, "real_vs_active": None}
        group1, group2, group3 = groups

        # omnibus friedman
        cols = [c for c in groups if c in df_paired.columns]
        df_omni = df_paired.dropna(subset=cols)

        if len(cols) == 3 and len(df_omni) > 2:
            fstat, fp = friedmanchisquare(
                df_omni[group1], df_omni[group2], df_omni[group3]
            )
            print(
                f"[Omnibus Friedman] (n={len(df_omni)}) -> chi2: {fstat:.4f}, p: {fp:.4f}"
            )
            results["friedman"] = {"chi2": fstat, "p_value": fp, "n": len(df_omni)}

        # real vs sham
        if group1 in df_paired.columns and group3 in df_paired.columns:
            df_g1g3 = df_paired.dropna(subset=[group1, group3])
            stat, p = self._wilcoxon(df_g1g3[group1].values, df_g1g3[group3].values)
            d = self._cohens_d_paired(df_g1g3[group1].values, df_g1g3[group3].values)
            print(
                f"[{group1} vs {group3}] (n={len(df_g1g3)}) -> W: {stat:.4f}, p: {p:.4f}, d: {d:.4f}"
            )

        # real vs active
        if group1 in df_paired.columns and group2 in df_paired.columns:
            df_g1g2 = df_paired.dropna(subset=[group1, group2])
            stat, p = self._wilcoxon(df_g1g2[group1].values, df_g1g2[group2].values)
            d = self._cohens_d_paired(df_g1g2[group1].values, df_g1g2[group2].values)
            print(
                f"[{group1} vs {group2}] (n={len(df_g1g2)}) -> W: {stat:.4f}, p: {p:.4f}, d: {d:.4f}"
            )

        return results

    def run_time_series_permutation(
        self, title, metric, time_pairs, group_a="Real", group_b="Sham"
    ):
        print(f"\n--- {title} ---")

        def mean_diff(x, y):
            return np.mean(x - y)

        for start_run, end_run in time_pairs:
            run_data = self.df[self.df[self.time_col].isin([start_run, end_run])]
            pivot_data = run_data.pivot_table(
                index=[self.subject_col, self.condition_col],
                columns=self.time_col,
                values=metric,
            ).reset_index()

            col_name = f"Growth_{start_run}_{end_run}"
            pivot_data[col_name] = pivot_data[end_run] - pivot_data[start_run]

            final_pivot = pivot_data.pivot(
                index=self.subject_col, columns=self.condition_col, values=col_name
            ).dropna()

            if group_a in final_pivot.columns and group_b in final_pivot.columns:
                res = permutation_test(
                    (final_pivot[group_a], final_pivot[group_b]),
                    mean_diff,
                    permutation_type="samples",
                    alternative="two-sided",
                )
                print(
                    f"Interval ({start_run} -> {end_run}): p-value = {res.pvalue:.4f}"
                )
