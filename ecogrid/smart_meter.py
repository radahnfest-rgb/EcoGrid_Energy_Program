import random
import time
import uuid

from .event_bus import EventBus
from .models import MeterReading
from .observability import Metrics


class SmartMeterIngestion:
    def __init__(self, event_bus: EventBus, metrics: Metrics) -> None:
        self.event_bus = event_bus
        self.metrics = metrics
        self._processed_reading_ids = set()

    def ingest(self, reading: MeterReading) -> bool:
        if reading.reading_id in self._processed_reading_ids:
            self.metrics.duplicate_readings += 1
            return False

        if not self._is_valid(reading):
            self.metrics.readings_rejected += 1
            return False

        self._processed_reading_ids.add(reading.reading_id)
        self.metrics.readings_received += 1

        self.event_bus.publish(
            "meter_reading_accepted",
            {
                "reading_id": reading.reading_id,
                "meter_id": reading.meter_id,
                "generated_kwh": reading.generated_kwh,
                "consumed_kwh": reading.consumed_kwh,
                "net_kwh": reading.net_kwh,
                "role": reading.role.value,
            },
        )
        return True

    @staticmethod
    def _is_valid(reading: MeterReading) -> bool:
        if not reading.meter_id.strip():
            return False
        if reading.generated_kwh < 0 or reading.consumed_kwh < 0:
            return False
        return True


class MeterSimulator:
    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)

    def create_reading(self, meter_id: str) -> MeterReading:
        generated = round(self.random.uniform(0.5, 8.0), 2)
        consumed = round(self.random.uniform(0.5, 8.0), 2)

        return MeterReading(
            reading_id=str(uuid.uuid4()),
            meter_id=meter_id,
            generated_kwh=generated,
            consumed_kwh=consumed,
            timestamp=time.time(),
        )

    def create_batch(self, meter_count: int) -> list[MeterReading]:
        return [
            self.create_reading(f"M{index:03d}")
            for index in range(1, meter_count + 1)
        ]
