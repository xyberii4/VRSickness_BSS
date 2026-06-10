class ScoreCalculator:
    # ssq weights (nausea, oculomotor, disorientation)
    SSQ_WEIGHTS = {
        "General discomfort": (1, 1, 0),
        "Fatigue": (0, 1, 0),
        "Headache": (0, 1, 0),
        "Eyestrain": (0, 1, 0),
        "Difficulty focusing": (0, 1, 1),
        "Increased salivation": (1, 0, 0),
        "Sweating": (1, 0, 0),
        "Nausea": (1, 0, 1),
        "Difficulty concentrating": (1, 1, 0),
        "Fullness of head": (0, 0, 1),
        "Blurred vision": (0, 1, 1),
        "Dizziness (eyes open)": (0, 0, 1),
        "Dizziness (eyes closed)": (0, 0, 1),
        "Vertigo": (0, 0, 1),
        "Stomach awareness": (1, 0, 0),
        "Burping": (1, 0, 0),
    }

    @classmethod
    def calculate_ssq(cls, ratings: dict) -> float:
        n_sum = o_sum = d_sum = 0
        for item, (n_w, o_w, d_w) in cls.SSQ_WEIGHTS.items():
            val = float(ratings.get(item, 0))
            n_sum += val * n_w
            o_sum += val * o_w
            d_sum += val * d_w

        return (n_sum + o_sum + d_sum) * 3.74

    @classmethod
    def calculate_vrsq(cls, ratings: dict) -> float:
        o_vr_items = [
            "General discomfort",
            "Fatigue",
            "Eyestrain",
            "Difficulty focusing",
        ]
        d_vr_items = [
            "Headache",
            "Fullness of head",
            "Blurred vision",
            "Dizziness (eyes closed)",
            "Vertigo",
        ]

        o_vr = sum(float(ratings.get(k, 0)) for k in o_vr_items)
        d_vr = sum(float(ratings.get(k, 0)) for k in d_vr_items)

        vrsq_o = (o_vr / 12.0) * 100
        vrsq_d = (d_vr / 15.0) * 100

        return (vrsq_o + vrsq_d) / 2.0

    @classmethod
    def calculate_csq(cls, ratings: dict) -> tuple[float, float]:
        def _csq_val(item_key):
            return min(float(ratings.get(item_key, 0)), 2.0)

        csq_dizziness = (
            _csq_val("Headache") * 0.50
            + _csq_val("Nausea") * 0.84
            + _csq_val("Dizziness (eyes open)") * 0.89
            + _csq_val("Dizziness (eyes closed)") * 0.99
            + _csq_val("Vertigo") * 0.54
        )

        csq_focusing = (
            _csq_val("Eyestrain") * 0.58
            + _csq_val("Difficulty focusing") * 0.89
            + _csq_val("Fullness of head") * 0.55
            + _csq_val("Blurred vision") * 0.81
        )

        return csq_dizziness, csq_focusing

    @classmethod
    def calculate_tolerability(cls, tol_data: dict, weight_val: float = 0.5) -> float:
        score = 0.0
        for item, values in tol_data.items():
            intensity = float(values.get("intensity", 0.0))
            affects_performance = bool(values.get("performance", False))

            weight = weight_val if affects_performance else 0.0
            score += intensity + (intensity * weight)

        return score
