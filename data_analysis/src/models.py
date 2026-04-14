from dataclasses import dataclass
from typing import List, Dict, Optional

import mne
import numpy as np


@dataclass
class EEGRecording:
    eeg_data: np.ndarray  # volts
    markers: np.ndarray
    timestamps: np.ndarray  # ms
    sampling_freq: float  # Hz

    def to_mne(self) -> mne.io.RawArray:
        reshaped = self.eeg_data.reshape(1, -1)

        info = mne.create_info(
            ch_names=["P3"], sfreq=self.sampling_freq, ch_types="eeg"
        )

        eeg_mne = mne.io.RawArray(reshaped, info)
        return eeg_mne


@dataclass
class Run:
    run_num: int
    eeg: EEGRecording
    fms: int  # 0-20
    clean_eeg: mne.io.RawArray
    epochs: mne.Epochs
    itc: Optional[float] = None


@dataclass
class Session:
    session_type: str  # Real, Active, Sham
    baseline_eeg: EEGRecording
    pre_ssq: float
    post_ssq: float
    runs: List[Run]
    baseline_epochs: mne.Epochs


@dataclass
class Participant:
    p_id: int
    vimssq: int
    sessions: Dict[str, Session]
