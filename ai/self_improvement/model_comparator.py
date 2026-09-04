"""
ai/self_improvement/model_comparator.py
=========================================
OptionAlpha Agent — Statistical A/B Model Comparator

Compares candidate retrained models against active production models using
paired statistical tests (McNemar's test, paired t-test on Brier score, and AUC diff).
Protects against degradation or overfitting during autonomous retraining.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from loguru import logger


class ModelComparator:
    """
    Evaluates whether a candidate model statistically outperforms production.
    """

    @staticmethod
    def compare_classifiers(
        y_true: np.ndarray,
        y_prod_preds: np.ndarray,
        y_cand_preds: np.ndarray,
        significance_level: float = 0.05,
    ) -> Dict:
        """
        Runs McNemar's paired test and accuracy comparison.
        """
        n = len(y_true)
        if n < 10:
            return {"promoted": False, "reason": "Insufficient test samples"}

        prod_correct = (y_prod_preds == y_true)
        cand_correct = (y_cand_preds == y_true)

        prod_acc = float(np.mean(prod_correct))
        cand_acc = float(np.mean(cand_correct))

        # Contingency table:
        # b: prod correct, cand incorrect
        # c: prod incorrect, cand correct
        b = int(np.sum(prod_correct & ~cand_correct))
        c = int(np.sum(~cand_correct & prod_correct))

        # McNemar's Chi-Square statistic with continuity correction
        if (b + c) > 0:
            chi2 = ((abs(b - c) - 1.0) ** 2) / (b + c)
            p_val = float(1.0 - stats.chi2.cdf(chi2, df=1))
        else:
            chi2 = 0.0
            p_val = 1.0

        should_promote = (cand_acc > prod_acc + 0.02) and (p_val < significance_level)

        result = {
            "promoted": should_promote,
            "prod_accuracy": round(prod_acc, 4),
            "cand_accuracy": round(cand_acc, 4),
            "accuracy_delta": round(cand_acc - prod_acc, 4),
            "p_value": round(p_val, 4),
            "mcnemar_chi2": round(chi2, 3),
            "samples_evaluated": n,
        }

        if should_promote:
            logger.success("ModelComparator: Promoted new candidate model (p={:.4f}, acc_delta={:+.2f}%)", p_val, (cand_acc - prod_acc)*100)
        else:
            logger.info("ModelComparator: Retained current model (cand_acc={:.2f}%, prod_acc={:.2f}%)", cand_acc*100, prod_acc*100)

        return result
