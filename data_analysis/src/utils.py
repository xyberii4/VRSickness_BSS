import numpy as np
import pandas as pd

SESSIONS = ["Real", "Active", "Sham"]


def print_itc_summary(dataset):
    print("\n--- ITC (normalized) ---")
    session_types = ["Real", "Active", "Sham"]

    for s_type in session_types:
        itc_values = []
        for p in dataset.values():
            if s_type in p.sessions:
                for run in p.sessions[s_type].runs:
                    if hasattr(run, "itc") and run.itc is not None:
                        if not np.isnan(run.itc):
                            itc_values.append(run.itc)

        if itc_values:
            arr = np.array(itc_values)
            print(f"[{s_type}]")
            print(
                f"  Avg 18Hz ITC: {np.mean(arr):.4f} ± {np.std(arr):.4f} (n={len(arr)} runs)"
            )
        else:
            print(f"[{s_type}]")
            print("  Avg 18Hz ITC: No valid data")


def extract_features_to_dataframe(dataset):
    """flatten dataset into a 2D pandas df"""
    rows = []
    for p_id, participant in dataset.items():
        for session_name, session in participant.sessions.items():
            for run in session.runs:
                rows.append(
                    {
                        "Participant_ID": p_id,
                        "VIMSSQ_Score": participant.vimssq,
                        "Session_Type": session_name,
                        "Run_Number": run.run_num,
                        "Pre_SSQ": session.pre_ssq,
                        "Post_SSQ": session.post_ssq,
                        "FMS": run.fms,
                        "ITC_Norm": getattr(run, "itc", np.nan),
                    }
                )
    return pd.DataFrame(rows)


def print_dataset_summary(dataset):
    print(f"Total participants processed: {len(dataset)}")

    # epoch metrics
    total_created = 0
    total_retained = 0

    for p in dataset.values():
        for session in p.sessions.values():
            for run in session.runs:
                if run.epochs is not None:
                    total_created += len(run.epochs.drop_log)
                    total_retained += len(run.epochs)

    if total_created > 0:
        dropped = total_created - total_retained
        drop_rate = (dropped / total_created) * 100
        print("\n--- Artifact Rejection ---")
        print(f"Total epochs:   {total_created}")
        print(f"Retained epochs: {total_retained}")
        print(f"Drop rate:     {drop_rate:.2f}%")

    # behavioural metrics
    print("\n--- Behavioral Metrics ---")

    for s in SESSIONS:
        final_fms_scores = []
        ssq_shifts = []

        for p in dataset.values():
            if s in p.sessions:
                session = p.sessions[s]

                # final fms
                final_run = next((r for r in session.runs if r.run_num == 3), None)
                if final_run is not None and final_run.fms is not None:
                    if not np.isnan(final_run.fms):
                        final_fms_scores.append(final_run.fms)

                # ssq shift
                pre = session.pre_ssq
                post = session.post_ssq
                if pre is not None and post is not None:
                    if not np.isnan(pre) and not np.isnan(post):
                        ssq_shift = post - pre
                        ssq_shifts.append(ssq_shift)

        print(f"[{s}]")

        # fms
        if final_fms_scores:
            fms_arr = np.array(final_fms_scores)
            print(
                f"  Final fms (run 3):    {np.mean(fms_arr):.2f} ± {np.std(fms_arr):.2f} (n={len(fms_arr)})"
            )
        else:
            print("  Final fms (run 3):    no valid data")

        # ssq
        if ssq_shifts:
            ssq_arr = np.array(ssq_shifts)
            print(
                f"  SSQ shift (post-pre): {np.mean(ssq_arr):+.2f} ± {np.std(ssq_arr):.2f} (n={len(ssq_arr)})"
            )
        else:
            print("  SSQ shift (post-pre): no valid data")
