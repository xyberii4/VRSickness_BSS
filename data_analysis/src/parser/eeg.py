from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.models import EEGRecording


class EEGParser:
    def __init__(self, sampling_freq=500, channel=2, channel_name="P3"):
        self.sampling_freq = sampling_freq
        self.channel = channel  # electorde 3
        self.channel_name = channel_name

    def load_easy(self, easy_path: str | Path):
        cols_to_read = [self.channel, 11, 12]

        df = pd.read_csv(
            easy_path, sep="\t", usecols=cols_to_read, header=None, engine="pyarrow"
        )

        arr = df.to_numpy()

        eeg_data = arr[:, 0] * 1e-9  # convert to volts
        markers = arr[:, 1]
        timestamps = arr[:, 2]

        return EEGRecording(eeg_data, markers, timestamps, self.sampling_freq)

    def get_section(self, eeg_rec: EEGRecording, marker: int):
        marker_idx = np.where(eeg_rec.markers == marker)[0]

        start = marker_idx[0]
        end = marker_idx[-1] + 1

        eeg_data = eeg_rec.eeg_data[start:end]
        markers = eeg_rec.markers[start:end]
        timestamps = eeg_rec.timestamps[start:end]

        return EEGRecording(eeg_data, markers, timestamps, self.sampling_freq)

    def get_between(self, eeg_rec: EEGRecording, start_ts: float, end_ts: float):
        timestamp_idx = np.where(
            (eeg_rec.timestamps >= start_ts) & (eeg_rec.timestamps < end_ts)
        )[0]

        start = timestamp_idx[0]
        end = timestamp_idx[-1] + 1

        eeg_data = eeg_rec.eeg_data[start:end]
        markers = eeg_rec.markers[start:end]
        timestamps = eeg_rec.timestamps[start:end]

        return EEGRecording(eeg_data, markers, timestamps, self.sampling_freq)

    def concatenate(self, eeg_recs: list):
        """combine multiple EEGRecordings into single recording."""
        eeg_data = np.concatenate([rec.eeg_data for rec in eeg_recs], axis=0)
        markers = np.concatenate([rec.markers for rec in eeg_recs], axis=0)
        timestamps = np.concatenate([rec.timestamps for rec in eeg_recs], axis=0)

        return EEGRecording(eeg_data, markers, timestamps, eeg_recs[0].sampling_freq)

    def plot_data(self, eeg_recs: list, labels: list, title="eeg comparison"):
        fig, ax = plt.subplots(figsize=(12, 4))

        for rec_idx, eeg_rec in enumerate(eeg_recs):
            # align to relative start and convert ms to seconds
            time_axis = (eeg_rec.timestamps - eeg_rec.timestamps[0]) / 1000.0

            ax.plot(
                time_axis,
                eeg_rec.eeg_data,
                linewidth=0.8,
                alpha=0.7,
                label=labels[rec_idx],
            )

        ax.set_ylabel(f"{self.channel_name}\n(V)", rotation=0, labelpad=20, ha="right")
        ax.set_xlabel("time (seconds)")
        ax.grid(True, alpha=0.3)

        ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.05),
            ncol=len(eeg_recs),
            frameon=False,
        )

        fig.suptitle(title, y=1.15, fontsize=14)

        plt.tight_layout()
        plt.show()
