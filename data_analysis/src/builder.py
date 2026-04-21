import mne
from pathlib import Path

from src.models import EEGRecording, Run, Session, Participant
from src.parser.eeg import EEGParser
from src.parser.scores import ScoreParser

SESSIONS = ["Real", "Active", "Sham"]


class DatasetBuilder:
    def __init__(
        self,
        raw_dir: str,
        l_freq=1.0,
        h_freq=40.0,
        notch_freq=50.0,
        epoch_dur=2.0,
        reject_thresh=1e-4,
    ):
        self.raw_dir = Path(raw_dir)
        self.eeg_parser = EEGParser()
        self.score_parser = ScoreParser(self.raw_dir / "metadata.xlsx")

        self.l_freq = l_freq
        self.h_freq = h_freq
        self.notch_freq = notch_freq
        self.epoch_dur = epoch_dur
        self.reject_criteria = dict(eeg=reject_thresh)

    def _filter_noise(self, eeg_data: mne.io.RawArray):
        cleaned = eeg_data.copy()
        cleaned.notch_filter(freqs=self.notch_freq)
        cleaned.filter(l_freq=self.l_freq, h_freq=self.h_freq)
        return cleaned

    def _create_epochs(self, eeg_data: mne.io.RawArray):
        epochs = mne.make_fixed_length_epochs(
            eeg_data, duration=self.epoch_dur, preload=True
        )

        # remove artifacts
        epochs.drop_bad(reject=self.reject_criteria)
        return epochs

    def build(self):
        participants = {}

        for p_dir in self.raw_dir.iterdir():
            if p_dir.is_dir() and p_dir.name.isdigit():
                p_id = int(p_dir.name)

                p = self._build_participant(p_id)
                participants[p_id] = p

        return participants

    def _build_participant(self, p_id: int):
        vimssq = self.score_parser.get_vimssq(p_id)
        sessions = {}

        for s in SESSIONS:
            session = self._build_session(p_id, s)

            if session is not None:
                sessions[s] = session

        return Participant(p_id=p_id, vimssq=vimssq, sessions=sessions)

    def _build_session(self, p_id: int, session_type: str):
        tag = f"{p_id}_{session_type}"
        p_dir = self.raw_dir / str(p_id)

        easy_fn = p_dir / f"{tag}.easy"
        csv_fn = p_dir / f"{tag}.csv"
        ssq_fn = p_dir / f"{tag}_SSQ.xlsx"
        tol_fn = p_dir / f"{tag}_Safety_and_Tolerability.docx"

        if (
            not easy_fn.exists()
            or not csv_fn.exists()
            or not ssq_fn.exists()
            or not tol_fn.exists()
        ):
            print(
                f"warning: missing files for participant {p_id}, session '{session_type}'. skipped"
            )
            return None

        raw_eeg = self.eeg_parser.load_easy(easy_fn)

        clean_mne = self._filter_noise(raw_eeg.to_mne())

        clean_eeg = EEGRecording(
            eeg_data=clean_mne.get_data()[0],
            markers=raw_eeg.markers,
            timestamps=raw_eeg.timestamps,
            sampling_freq=raw_eeg.sampling_freq,
        )

        baseline_eeg = self.eeg_parser.get_section(clean_eeg, 1)
        baseline_mne = baseline_eeg.to_mne()
        baseline_epochs = self._create_epochs(baseline_mne)

        events, fms_scores = self.score_parser.parse_session_csv(csv_fn)
        sickness_scores = self.score_parser.get_sickness_scores(ssq_fn)
        tolerability_score = self.score_parser.get_tolerability_score(tol_fn)

        runs = []

        for i in range(1, 4):
            start_ts = events[f"Run_{i}_Start"]
            end_ts = events[f"Break_{i}_Start"]

            fms = fms_scores[i]

            run = self._build_run(raw_eeg, clean_eeg, i, start_ts, end_ts, fms)

            runs.append(run)

        return Session(
            session_type=session_type,
            baseline_eeg=baseline_eeg,
            pre_sickness=sickness_scores.get("Pre"),
            post_sickness=sickness_scores.get("Post"),
            tolerability=tolerability_score,
            runs=runs,
            baseline_epochs=baseline_epochs,
        )

    def _build_run(
        self,
        raw_eeg: EEGRecording,
        clean_eeg: EEGRecording,
        run_num: int,
        start_ts: float,
        end_ts: float,
        fms: int,
    ):
        run_raw = self.eeg_parser.get_between(raw_eeg, start_ts, end_ts)
        run_clean = self.eeg_parser.get_between(clean_eeg, start_ts, end_ts)

        run_clean_mne = run_clean.to_mne()

        epochs = self._create_epochs(run_clean_mne)

        return Run(
            run_num=run_num,
            eeg=run_raw,
            fms=fms,
            clean_eeg=run_clean_mne,
            epochs=epochs,
        )
