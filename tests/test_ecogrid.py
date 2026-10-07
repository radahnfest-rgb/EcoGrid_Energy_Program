import unittest
from decimal import Decimal

from ecogrid.event_bus import EventBus
from ecogrid.marketplace import Marketplace
from ecogrid.models import MeterReading, Trade
from ecogrid.observability import Metrics
from ecogrid.settlement import SettlementService
from ecogrid.smart_meter import SmartMeterIngestion


class EcoGridTests(unittest.TestCase):
    def test_invalid_reading_is_rejected(self):
        bus = EventBus()
        metrics = Metrics()
        ingestion = SmartMeterIngestion(bus, metrics)

        reading = MeterReading(
            reading_id="r1",
            meter_id="M001",
            generated_kwh=-1.0,
            consumed_kwh=2.0,
            timestamp=0.0,
        )

        self.assertFalse(ingestion.ingest(reading))
        self.assertEqual(metrics.readings_rejected, 1)

    def test_duplicate_reading_is_blocked(self):
        bus = EventBus()
        metrics = Metrics()
        ingestion = SmartMeterIngestion(bus, metrics)

        reading = MeterReading(
            reading_id="r1",
            meter_id="M001",
            generated_kwh=3.0,
            consumed_kwh=2.0,
            timestamp=0.0,
        )

        self.assertTrue(ingestion.ingest(reading))
        self.assertFalse(ingestion.ingest(reading))
        self.assertEqual(metrics.duplicate_readings, 1)

    def test_marketplace_matches_seller_and_buyer(self):
        bus = EventBus()
        metrics = Metrics()
        marketplace = Marketplace(bus, metrics)

        marketplace.handle_meter_event(
            {"meter_id": "S1", "net_kwh": 2.0}
        )
        marketplace.handle_meter_event(
            {"meter_id": "B1", "net_kwh": -1.5}
        )

        trades = marketplace.match_orders()

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].quantity_kwh, 1.5)

    def test_settlement_is_idempotent(self):
        metrics = Metrics()
        settlement = SettlementService(metrics)

        trade = Trade(
            trade_id="T1",
            seller_meter_id="S1",
            buyer_meter_id="B1",
            quantity_kwh=2.0,
            price_per_kwh=Decimal("0.30"),
        )

        first = settlement.settle(trade)
        second = settlement.settle(trade)

        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertEqual(len(settlement.records), 1)
        self.assertEqual(metrics.settlement_duplicates_prevented, 1)


if __name__ == "__main__":
    unittest.main()
