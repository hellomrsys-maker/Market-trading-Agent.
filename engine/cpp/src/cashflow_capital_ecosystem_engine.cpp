#include "state_vector.h"
#include <vector>
#include <numeric>

namespace optionalpha {

class CashflowCapitalEcosystemEngine {
public:
    explicit CashflowCapitalEcosystemEngine(AtomicStateVector& state) : state_(state) {}

    // Simple cashflow allocation demo: allocate income proportionally to savings and expenses
    void allocate(double income, double expenseRatio) {
        double expenses = income * expenseRatio;
        double savings = income - expenses;
        // Store results in shared state (using price for expense, volatility for savings for demo)
        state_.price = expenses;
        state_.volatility = savings;
    }

private:
    AtomicStateVector& state_;
};

} // namespace optionalpha
