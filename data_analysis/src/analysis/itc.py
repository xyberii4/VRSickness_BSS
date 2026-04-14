import mne
import numpy as np


class ITCCalculator:
    def __init__(self, target_freq=18.0, cycle_num=9.0):
        self.target_freq = np.array([target_freq])
        self.cycle_num = cycle_num

    def get_itc(self, epochs: mne.Epochs):
        tfr, itc = epochs.compute_tfr(
            method="morlet",
            freqs=self.target_freq,
            return_itc=True,
            average=True,
            n_cycles=self.cycle_num,
        )

        itc_mean = np.mean(itc.data[0, 0, :])

        return float(itc_mean)

    def normalize_itc(self, active_itc: float, baseline_itc: float):
        return np.log10(active_itc / baseline_itc)
