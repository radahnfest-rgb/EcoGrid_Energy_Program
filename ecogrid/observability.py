from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class Metrics:
    readings_received: int = 0
    readings_rejected: int = 0
    duplicate_readings: int = 0
    trades_created: int = 0
    settlements_completed: int = 0
    settlement_duplicates_prevented: int = 0
    events_processed: int = 0
    started_at: float = field(default_factory=perf_counter)

    @property
    def elapsed_seconds(self) -> float:
        return max(perf_counter() - self.started_at, 0.000001)

    @property
    def readings_per_second(self) -> float:
        return self.readings_received / self.elapsed_seconds
