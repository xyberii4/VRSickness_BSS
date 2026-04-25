import mne
import numpy as np

from src.builder import DatasetBuilder
from src.analysis.itc import ITCCalculator
from src.analysis.stats import StatisticalAnalyzer
from src.visualizer import Visualizer
from src.utils import (
    print_itc_summary,
    extract_features_to_dataframe,
    print_dataset_summary,
)

VERBOSE = False


def main():
    mne.set_log_level(VERBOSE)
    builder = DatasetBuilder("data/raw")
    itc_calc = ITCCalculator()

    dataset = builder.build()

    for p_id, participant in dataset.items():
        for session in participant.sessions.values():
            # baseline itc
            if session.baseline_epochs is not None and len(session.baseline_epochs) > 0:
                baseline_itc = itc_calc.get_itc(session.baseline_epochs)
            else:
                baseline_itc = np.nan

            # run itc
            for run in session.runs:
                if (
                    run.epochs is not None
                    and len(run.epochs) > 0
                    and not np.isnan(baseline_itc)
                ):
                    raw_itc = itc_calc.get_itc(run.epochs)
                    run.itc = itc_calc.normalize_itc(raw_itc, baseline_itc)
                else:
                    run.itc = np.nan

    df = extract_features_to_dataframe(dataset)

    metrics_to_test = [
        "SSQ_Total",
        "SSQ_Nausea",
        "SSQ_Oculomotor",
        "SSQ_Disorientation",
        "VRSQ_Total",
        "VRSQ_Disorientation",
        "VRSQ_Oculomotor",
        "CSQ_Dizziness",
        "CSQ_Difficulty_Focusing",
    ]

    df["Is_Real"] = (df["Session_Type"] == "Real").astype(int)

    for metric in metrics_to_test:
        pre_col = f"Pre_{metric}"
        post_col = f"Post_{metric}"
        shift_col = f"{metric}_Shift"

        if pre_col in df.columns and post_col in df.columns:
            df[shift_col] = df[post_col] - df[pre_col]

    df.to_excel("master.xlsx", index=False)

    print_dataset_summary(dataset)
    print_itc_summary(dataset)

    analyzer = StatisticalAnalyzer(df)

    # fms
    df_fms_paired = analyzer.get_delta("FMS", start_time=1, end_time=3)
    analyzer.run_test("FMS Growth (Run 3 - Run 1)", df_fms_paired)

    # itc
    df_itc_paired = analyzer.get_delta("ITC_Norm", start_time=1, end_time=3)
    analyzer.run_test("18Hz ITC Growth (Run 3 - Run 1)", df_itc_paired)

    # sickness scores with covar
    for metric in metrics_to_test:
        shift_col = f"{metric}_Shift"
        df_metric_paired = analyzer.get_score_shift(shift_col)
        analyzer.run_test(f"{metric} Shift", df_metric_paired)

        analyzer.partial_spearman(var1="Is_Real", var2=shift_col, covar="Tolerability")

    # itc vs fms
    analyzer.spearman_correlation(var1="ITC_Norm", var2="FMS")

    # fms trajectories
    analyzer.run_time_series_permutation(
        title="FMS In-Ride Trajectories (Permutation Test: Real vs Sham)",
        metric="FMS",
        time_pairs=[(1, 2), (2, 3), (1, 3)],
        group_a="Real",
        group_b="Sham",
    )

    print("\nGenerating Publication Plots...")
    visualizer = Visualizer(df)
    visualizer.generate_publication_plots()


if __name__ == "__main__":
    main()
