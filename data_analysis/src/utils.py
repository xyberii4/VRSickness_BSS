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
            session_base = {
                "Participant_ID": p_id,
                "VIMSSQ_Score": participant.vimssq,
                "Session_Type": session_name,
                "Tolerability": getattr(session, "tolerability", np.nan),
            }

            if hasattr(session, "pre_sickness") and session.pre_sickness:
                for score_name, value in session.pre_sickness.items():
                    session_base[f"Pre_{score_name}"] = value

            if hasattr(session, "post_sickness") and session.post_sickness:
                for score_name, value in session.post_sickness.items():
                    session_base[f"Post_{score_name}"] = value

            for run in session.runs:
                row = session_base.copy()
                row["Run_Number"] = run.run_num
                row["FMS"] = run.fms
                row["ITC_Norm"] = getattr(run, "itc", np.nan)

                rows.append(row)

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

    metrics_to_track = [
        "SSQ_Total",
        "VRSQ_Total",
        "CSQ_Dizziness",
        "CSQ_Difficulty_Focusing",
    ]

    for s in SESSIONS:
        fms_shifts = []

        shifts = {metric: [] for metric in metrics_to_track}

        for p in dataset.values():
            if s in p.sessions:
                session = p.sessions[s]

                # fms shift
                first_run = next((r for r in session.runs if r.run_num == 1), None)
                final_run = next((r for r in session.runs if r.run_num == 3), None)

                if first_run is not None and final_run is not None:
                    if first_run.fms is not None and final_run.fms is not None:
                        if not np.isnan(first_run.fms) and not np.isnan(final_run.fms):
                            fms_shifts.append(final_run.fms - first_run.fms)

                # sickness shifts
                for metric in metrics_to_track:
                    pre = session.pre_sickness.get(metric)
                    post = session.post_sickness.get(metric)

                    if pre is not None and post is not None:
                        if not np.isnan(pre) and not np.isnan(post):
                            shifts[metric].append(post - pre)

        print(f"[{s}]")

        # fms shift
        label_fms = "  FMS shift:"
        if fms_shifts:
            fms_shifts_np = np.array(fms_shifts)
            print(
                f"{label_fms:<32} {np.mean(fms_shifts_np):+.2f} ± {np.std(fms_shifts_np):.2f} (n={len(fms_shifts_np)})"
            )
        else:
            print(f"{label_fms:<32} no valid data")

        for metric in metrics_to_track:
            arr = shifts[metric]

            label = f"  {metric} shift:"

            if arr:
                arr_np = np.array(arr)
                print(
                    f"{label:<32} {np.mean(arr_np):+.2f} ± {np.std(arr_np):.2f} (n={len(arr_np)})"
                )
            else:
                print(f"{label:<32} no valid data")
