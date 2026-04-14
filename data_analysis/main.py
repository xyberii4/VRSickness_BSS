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
    df.to_csv("dataset.csv", index=False)

    analyzer = StatisticalAnalyzer(df)

    print_dataset_summary(dataset)
    print_itc_summary(dataset)

    # fms
    df_fms_paired = analyzer.get_delta("FMS")
    analyzer.run_test("FMS Growth (Run 3 - Run 1)", df_fms_paired)

    # ssq
    df_ssq_paired = analyzer.get_ssq_shift()
    analyzer.run_test("SSQ Shift", df_ssq_paired)

    # itc
    df_itc_paired = analyzer.get_delta("ITC_Norm")
    analyzer.run_test("18Hz ITC Growth (Run 3 - Run 1)", df_itc_paired)

    analyzer.run_spearman_correlation()

    print("\nGenerating Publication Plots...")
    visualizer = Visualizer(df)
    visualizer.generate_publication_plots()


if __name__ == "__main__":
    main()
