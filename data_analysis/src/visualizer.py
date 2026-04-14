import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr


class Visualizer:
    def __init__(self, df):
        self.df = df
        self.palette = {"Real": "#029e73", "Active": "#d55e00", "Sham": "#999999"}
        self.treatment_order = ["Real", "Active", "Sham"]
        self._set_publication_style()

    def _set_publication_style(self):
        sns.set_theme(style="whitegrid", context="paper")
        plt.rcParams.update(
            {
                "axes.titlesize": 14,
                "axes.labelsize": 12,
                "xtick.labelsize": 10,
                "ytick.labelsize": 10,
            }
        )

    @staticmethod
    def _draw_stat_bracket(ax, x1, x2, y, h, text):
        ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c="black")
        ax.text(
            (x1 + x2) * 0.5,
            y + h + (h * 0.2),
            text,
            ha="center",
            va="bottom",
            color="black",
            fontsize=12,
        )

    def generate_publication_plots(self, output_dir="results"):
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        plots = {
            "plot_1_biomarker_correlation.png": self._plot_biomarker_correlation,
            "plot_2_sickness_trajectory.png": self._plot_sickness_trajectory,
            "plot_3_behavioral_outcome.png": self._plot_behavioral_outcome,
            "plot_4_neurological_outcome.png": self._plot_neurological_outcome,
        }

        print(f"\nGenerating and saving plots to '{out_path}/'...")

        for filename, plot_func in plots.items():
            fig, ax = plt.subplots(figsize=(8, 6))

            plot_func(ax)

            sns.despine()
            fig.tight_layout()

            fig.savefig(out_path / filename, dpi=300, bbox_inches="tight")

            print(f"Saved: {filename}")

        plt.show()

    def _plot_biomarker_correlation(self, ax):
        """scatter plot with spearman correlation"""
        corr_df = self.df.dropna(subset=["ITC_Norm", "FMS"])

        sns.regplot(
            data=corr_df,
            x="ITC_Norm",
            y="FMS",
            ax=ax,
            scatter_kws={
                "s": 60,
                "alpha": 0.7,
                "edgecolor": "k",
                "color": self.palette["Real"],
            },
            line_kws={"color": "black", "linewidth": 1.5},
        )

        rho, p_val = spearmanr(corr_df["ITC_Norm"], corr_df["FMS"])
        stats_text = f"Spearman's $\\rho$ = {rho:.2f}\n$p$ = {p_val:.3f}"
        ax.text(
            0.05,
            0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="gray"),
        )

        ax.set_title("18Hz ITC vs FMS", fontweight="bold")
        ax.set_xlabel("18 Hz Phase Coherence (Normalized)")
        ax.set_ylabel("Fast Motion Sickness (FMS) Score")

    def _plot_sickness_trajectory(self, ax):
        """sickness over runs 1, 2, and 3"""
        sns.pointplot(
            data=self.df,
            x="Run_Number",
            y="FMS",
            hue="Session_Type",
            ax=ax,
            palette=self.palette,
            markers=["o", "s", "D"],
            errorbar="se",
            capsize=0.1,
            dodge=0.1,
        )
        ax.set_title("FMS Over Time", fontweight="bold")
        ax.set_xlabel("Run Number")
        ax.set_ylabel("FMS Score (Mean ± SEM)")
        ax.legend(title="Treatment", frameon=False)

    def _plot_behavioral_outcome(self, ax):
        """box and swarm plot of post-pre ssq shift"""
        df_ssq = (
            self.df[["Participant_ID", "Session_Type", "Pre_SSQ", "Post_SSQ"]]
            .drop_duplicates()
            .copy()
        )
        df_ssq["SSQ_Shift"] = df_ssq["Post_SSQ"] - df_ssq["Pre_SSQ"]
        df_ssq = df_ssq.dropna(subset=["SSQ_Shift"])

        sns.boxplot(
            data=df_ssq,
            x="Session_Type",
            y="SSQ_Shift",
            hue="Session_Type",
            legend=False,
            order=self.treatment_order,
            palette=self.palette,
            showfliers=False,
            boxprops=dict(alpha=0.6),
            ax=ax,
        )
        sns.swarmplot(
            data=df_ssq,
            x="Session_Type",
            y="SSQ_Shift",
            order=self.treatment_order,
            color="black",
            alpha=0.8,
            size=6,
            ax=ax,
        )

        ax.set_title("Total Sickness Shift", fontweight="bold")
        ax.set_xlabel("Treatment Condition")
        ax.set_ylabel("Δ SSQ Score (Post - Pre)")

        if not df_ssq.empty:
            max_y = df_ssq["SSQ_Shift"].max()
            self._draw_stat_bracket(
                ax, x1=0, x2=2, y=max_y + 5, h=2, text="* $p = 0.031$"
            )

    def _plot_neurological_outcome(self, ax):
        """box and swarm plot of itc growth"""
        df_runs = self.df[self.df["Run_Number"].isin([1, 3])].copy()
        df_itc = df_runs.pivot(
            index=["Participant_ID", "Session_Type"],
            columns="Run_Number",
            values="ITC_Norm",
        ).reset_index()

        df_itc["ITC_Growth"] = df_itc[3] - df_itc[1]
        df_itc = df_itc.dropna(subset=["ITC_Growth"])

        sns.boxplot(
            data=df_itc,
            x="Session_Type",
            y="ITC_Growth",
            hue="Session_Type",
            legend=False,
            order=self.treatment_order,
            palette=self.palette,
            showfliers=False,
            boxprops=dict(alpha=0.6),
            ax=ax,
        )
        sns.swarmplot(
            data=df_itc,
            x="Session_Type",
            y="ITC_Growth",
            order=self.treatment_order,
            color="black",
            alpha=0.8,
            size=6,
            ax=ax,
        )

        ax.set_title("18Hz ITC (Brainwave Disruption)", fontweight="bold")
        ax.set_xlabel("Treatment Condition")
        ax.set_ylabel("Δ 18 Hz ITC (Run 3 - Run 1)")

        if not df_itc.empty:
            max_y_itc = df_itc["ITC_Growth"].max()
            self._draw_stat_bracket(
                ax, x1=0, x2=1, y=max_y_itc + 0.1, h=0.05, text="$d = -0.68$"
            )
