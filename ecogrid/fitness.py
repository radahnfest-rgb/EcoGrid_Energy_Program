from dataclasses import dataclass

from .observability import Metrics


@dataclass
class FitnessResult:
    name: str
    passed: bool
    details: str


def evaluate_fitness(
    metrics: Metrics,
    target_throughput: float = 100.0,
) -> list[FitnessResult]:
    results = []

    results.append(
        FitnessResult(
            name="No invalid readings accepted",
            passed=metrics.readings_rejected == 0,
            details=f"Rejected readings: {metrics.readings_rejected}",
        )
    )

    results.append(
        FitnessResult(
            name="No duplicate settlement",
            passed=metrics.settlement_duplicates_prevented == 0,
            details=(
                "Duplicate settlements prevented: "
                f"{metrics.settlement_duplicates_prevented}"
            ),
        )
    )

    results.append(
        FitnessResult(
            name="All created trades settled",
            passed=metrics.trades_created == metrics.settlements_completed,
            details=(
                f"Trades: {metrics.trades_created}, "
                f"settlements: {metrics.settlements_completed}"
            ),
        )
    )

    results.append(
        FitnessResult(
            name="Minimum ingestion throughput",
            passed=metrics.readings_per_second >= target_throughput,
            details=(
                f"{metrics.readings_per_second:.1f} readings/sec "
                f"(target {target_throughput:.1f})"
            ),
        )
    )

    return results
