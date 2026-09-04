// engine/cpp/regime_inference.hpp
// OptionAlpha Agent — C++20 Direct Tensor Inference for Regime Transformer (285K params)
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <vector>
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct RegimeProbabilities {
    double neutral;
    double bull_trend;
    double bear_trend;
    double high_iv_crisis;
    int32_t predicted_regime_idx;
};

class RegimeInferenceEngine {
public:
    static inline RegimeProbabilities softmax_classification(const double* logits_4) {
        double max_l = *std::max_element(logits_4, logits_4 + 4);
        double sum_e = 0.0;
        double exp_l[4];

        for (int i = 0; i < 4; ++i) {
            exp_l[i] = std::exp(logits_4[i] - max_l);
            sum_e += exp_l[i];
        }

        double p0 = exp_l[0] / sum_e;
        double p1 = exp_l[1] / sum_e;
        double p2 = exp_l[2] / sum_e;
        double p3 = exp_l[3] / sum_e;

        int32_t best_idx = 0;
        double max_p = p0;
        if (p1 > max_p) { max_p = p1; best_idx = 1; }
        if (p2 > max_p) { max_p = p2; best_idx = 2; }
        if (p3 > max_p) { max_p = p3; best_idx = 3; }

        return { p0, p1, p2, p3, best_idx };
    }
};

} // namespace optionalpha
