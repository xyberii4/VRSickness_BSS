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
                "axes.titlesize": 12,
                "axes.labelsize": 11,
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
            "fig_1_correlation_itc_fms.png": self._plot_biomarker_correlation,
            "fig_2_fms_trajectories.png": self._plot_sickness_trajectory,
            "fig_3_ssq_total_severity.png": self._plot_behavioral_outcome,
            "fig_4_itc_modulation.png": self._plot_neurological_outcome,
            "fig_5_ssq_subscale_profiles.png": self._plot_symptom_specificity,
            "fig_6_tolerability_covariate_analysis.png": self._plot_covariate_justification,
            "fig_7_fms_temporal_acceleration.png": self._plot_acceleration_profile,
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

        ax.set_title(
            "Correlation Between Parietal 18 Hz Phase Coherence and Fast Motion Sickness",
            fontweight="bold",
        )
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
        ax.set_title(
            "In-Ride Cybersickness Trajectories Across Sensory Stimulation Conditions",
            fontweight="bold",
        )
        ax.set_xlabel("Run Number")
        ax.set_ylabel("FMS Score (Mean ± SEM)")
        ax.legend(title="Treatment Condition", frameon=False)

    def _plot_behavioral_outcome(self, ax):
        """box and swarm plot of post-pre ssq shift"""
        df_ssq = (
            self.df[
                ["Participant_ID", "Session_Type", "Pre_SSQ_Total", "Post_SSQ_Total"]
            ]
            .drop_duplicates()
            .copy()
        )
        df_ssq["SSQ_Shift"] = df_ssq["Post_SSQ_Total"] - df_ssq["Pre_SSQ_Total"]
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

        ax.set_title(
            "Effect of Phase-Disrupted Sensory Stimulation on Total SSQ Severity",
            fontweight="bold",
        )
        ax.set_xlabel("Treatment Condition")
        ax.set_ylabel("Δ SSQ Total Score (Post - Pre)")

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

        ax.set_title(
            "Modulation of 18 Hz Inter-Trial Coherence (ITC) Across Experimental Runs",
            fontweight="bold",
        )
        ax.set_xlabel("Treatment Condition")
        ax.set_ylabel("Δ 18 Hz ITC (Run 3 - Run 1)")

    def _plot_symptom_specificity(self, ax):
        """grouped box and swarm plot of ssq sub-scales"""
        df_sub = (
            self.df[
                [
                    "Participant_ID",
                    "Session_Type",
                    "Pre_SSQ_Nausea",
                    "Post_SSQ_Nausea",
                    "Pre_SSQ_Oculomotor",
                    "Post_SSQ_Oculomotor",
                    "Pre_SSQ_Disorientation",
                    "Post_SSQ_Disorientation",
                ]
            ]
            .drop_duplicates()
            .copy()
        )

        df_sub["Nausea"] = df_sub["Post_SSQ_Nausea"] - df_sub["Pre_SSQ_Nausea"]
        df_sub["Oculomotor"] = (
            df_sub["Post_SSQ_Oculomotor"] - df_sub["Pre_SSQ_Oculomotor"]
        )
        df_sub["Disorientation"] = (
            df_sub["Post_SSQ_Disorientation"] - df_sub["Pre_SSQ_Disorientation"]
        )

        df_melt = df_sub.melt(
            id_vars=["Participant_ID", "Session_Type"],
            value_vars=["Nausea", "Oculomotor", "Disorientation"],
            var_name="Subscale",
            value_name="Shift",
        )

        sns.boxplot(
            data=df_melt,
            x="Subscale",
            y="Shift",
            hue="Session_Type",
            order=["Nausea", "Oculomotor", "Disorientation"],
            hue_order=self.treatment_order,
            palette=self.palette,
            showfliers=False,
            boxprops=dict(alpha=0.6),
            ax=ax,
        )
        sns.swarmplot(
            data=df_melt,
            x="Subscale",
            y="Shift",
            hue="Session_Type",
            order=["Nausea", "Oculomotor", "Disorientation"],
            hue_order=self.treatment_order,
            color="black",
            alpha=0.8,
            size=5,
            dodge=True,
            ax=ax,
        )

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:3], labels[:3], title="Treatment Condition", frameon=False)
        ax.set_title(
            "Sub-Scale Analysis of Cybersickness Symptom Profiles", fontweight="bold"
        )
        ax.set_xlabel("SSQ Symptom Sub-scale")
        ax.set_ylabel("Δ Score (Post - Pre)")

    def _plot_covariate_justification(self, ax):
        """scatterplot with regression for tolerability vs ssq shift"""
        df_cov = (
            self.df[
                [
                    "Participant_ID",
                    "Session_Type",
                    "Tolerability",
                    "Pre_SSQ_Total",
                    "Post_SSQ_Total",
                ]
            ]
            .drop_duplicates()
            .copy()
        )

        df_cov["SSQ_Total_Shift"] = df_cov["Post_SSQ_Total"] - df_cov["Pre_SSQ_Total"]
        df_rs = df_cov[df_cov["Session_Type"].isin(["Real", "Sham"])]

        sns.scatterplot(
            data=df_rs,
            x="Tolerability",
            y="SSQ_Total_Shift",
            hue="Session_Type",
            hue_order=["Real", "Sham"],
            palette=self.palette,
            s=80,
            alpha=0.8,
            edgecolor="k",
            ax=ax,
        )
        sns.regplot(
            data=df_rs[df_rs["Session_Type"] == "Real"],
            x="Tolerability",
            y="SSQ_Total_Shift",
            scatter=False,
            color=self.palette["Real"],
            ax=ax,
            line_kws={"linewidth": 2},
        )
        sns.regplot(
            data=df_rs[df_rs["Session_Type"] == "Sham"],
            x="Tolerability",
            y="SSQ_Total_Shift",
            scatter=False,
            color=self.palette["Sham"],
            ax=ax,
            line_kws={"linewidth": 2},
        )

        ax.set_title(
            "Influence of Hardware Tolerability on Cybersickness Mitigation",
            fontweight="bold",
        )
        ax.set_xlabel("Tolerability Impact Score")
        ax.set_ylabel("Δ SSQ Total (Post - Pre)")
        ax.legend(title="Treatment Condition", frameon=False)

    def _plot_acceleration_profile(self, ax):
        """boxplot and swarmplot of fms intervals"""
        df_runs = self.df.pivot_table(
            index=["Participant_ID", "Session_Type"], columns="Run_Number", values="FMS"
        ).reset_index()

        df_runs["Run 1 → 2"] = df_runs[2] - df_runs[1]
        df_runs["Run 2 → 3"] = df_runs[3] - df_runs[2]

        df_melt = df_runs.melt(
            id_vars=["Participant_ID", "Session_Type"],
            value_vars=["Run 1 → 2", "Run 2 → 3"],
            var_name="Interval",
            value_name="Delta",
        )

        sns.boxplot(
            data=df_melt,
            x="Interval",
            y="Delta",
            hue="Session_Type",
            hue_order=self.treatment_order,
            palette=self.palette,
            showfliers=False,
            boxprops=dict(alpha=0.6),
            ax=ax,
        )
        sns.swarmplot(
            data=df_melt,
            x="Interval",
            y="Delta",
            hue="Session_Type",
            hue_order=self.treatment_order,
            color="black",
            alpha=0.8,
            size=5,
            dodge=True,
            ax=ax,
        )

        ax.axhline(0, color="red", linestyle="--", linewidth=1.5, alpha=0.7, zorder=0)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:3], labels[:3], title="Treatment Condition", frameon=False)
        ax.set_title(
            "Temporal Acceleration Profiles of Fast Motion Sickness", fontweight="bold"
        )
        ax.set_xlabel("In-Ride Time Interval")
        ax.set_ylabel("Δ FMS Score (Acceleration Growth)")
