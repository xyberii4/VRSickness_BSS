from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import mne


@dataclass
class EEGRecording:
    raw: mne.io.RawArray
    markers: np.ndarray
    timestamps: np.ndarray  # ms


class EEGProcessor:
    def __init__(
        self,
        sampling_freq=500,
        channel=2,
        channel_name="P3",
        l_freq=1.0,
        h_freq=40.0,
        notch_freq=50.0,
        epoch_dur=2.0,
        reject_thresh=1e-4,
        target_freq=18.0,
        cycle_num=9.0,
    ):
        self.sampling_freq = sampling_freq
        self.channel = channel
        self.channel_name = channel_name
        self.l_freq = l_freq
        self.h_freq = h_freq
        self.notch_freq = notch_freq
        self.epoch_dur = epoch_dur
        self.reject_criteria = dict(eeg=reject_thresh)
        self.target_freq = np.array([target_freq])
        self.cycle_num = cycle_num

    def load_easy(self, easy_path: str | Path) -> EEGRecording:
        """parse Neuroelectrics .easy file and converts to MNE RawArray"""
        cols_to_read = [self.channel, 11, 12]
        df = pd.read_csv(
            easy_path, sep="\t", usecols=cols_to_read, header=None, engine="pyarrow"
        )
        arr = df.to_numpy()
        eeg_data = arr[:, 0] * 1e-9  # convert to volts
        markers = arr[:, 1]
        timestamps = arr[:, 2]

        info = mne.create_info(
            ch_names=[self.channel_name], sfreq=self.sampling_freq, ch_types="eeg"
        )
        raw = mne.io.RawArray(eeg_data.reshape(1, -1), info, verbose=False)

        return EEGRecording(raw, markers, timestamps)

    def filter_noise(self, eeg_rec: EEGRecording) -> EEGRecording:
        """apply notch and bandpass filters"""
        cleaned_raw = eeg_rec.raw.copy()
        cleaned_raw.notch_filter(freqs=self.notch_freq, verbose=False)
        cleaned_raw.filter(l_freq=self.l_freq, h_freq=self.h_freq, verbose=False)

        return EEGRecording(cleaned_raw, eeg_rec.markers, eeg_rec.timestamps)

    def get_section_by_marker(self, eeg_rec: EEGRecording, marker: int):
        marker_idx = np.where(eeg_rec.markers == marker)[0]
        if len(marker_idx) == 0:
            raise ValueError(f"Marker {marker} not found.")

        start = marker_idx[0]
        end = marker_idx[-1] + 1

        sliced_data = eeg_rec.raw.get_data(start=start, stop=end)
        sliced_raw = mne.io.RawArray(sliced_data, eeg_rec.raw.info, verbose=False)

        return EEGRecording(
            sliced_raw,
            eeg_rec.markers[start:end],
            eeg_rec.timestamps[start:end],
        )

    def get_section_by_timestamp(
        self, eeg_rec: EEGRecording, start_ts: float, end_ts: float
    ) -> EEGRecording:
        timestamp_idx = np.where(
            (eeg_rec.timestamps >= start_ts) & (eeg_rec.timestamps < end_ts)
        )[0]

        if len(timestamp_idx) == 0:
            raise ValueError(f"No data found between {start_ts} and {end_ts}")

        start = timestamp_idx[0]
        end = timestamp_idx[-1] + 1

        sliced_data = eeg_rec.raw.get_data(start=start, stop=end)
        sliced_raw = mne.io.RawArray(sliced_data, eeg_rec.raw.info, verbose=False)

        return EEGRecording(
            sliced_raw,
            eeg_rec.markers[start:end],
            eeg_rec.timestamps[start:end],
        )

    def create_epochs(self, eeg_rec: EEGRecording) -> mne.Epochs:
        epochs = mne.make_fixed_length_epochs(
            eeg_rec.raw, duration=self.epoch_dur, preload=True, verbose=False
        )
        epochs.drop_bad(reject=self.reject_criteria, verbose=False)

        return epochs

    def calculate_itc(self, epochs: mne.Epochs):
        tfr, itc = epochs.compute_tfr(
            method="morlet",
            freqs=self.target_freq,
            return_itc=True,
            average=True,
            n_cycles=self.cycle_num,
        )

        itc_mean = np.mean(itc.data[0, 0, :])

        return float(itc_mean)

    def normalize_itc(self, itc1, itc2):
        return np.log10(itc1 / itc2)
