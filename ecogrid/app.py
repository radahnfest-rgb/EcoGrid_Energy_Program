from decimal import Decimal

from .event_bus import EventBus
from .fitness import evaluate_fitness
from .marketplace import Marketplace
from .observability import Metrics
from .settlement import SettlementService
from .smart_meter import MeterSimulator, SmartMeterIngestion


def _ask_meter_count() -> int:
    while True:
        raw = input("Number of smart meters to simulate [10]: ").strip()

        if not raw:
            return 10

        try:
            value = int(raw)
            if 1 <= value <= 5000:
                return value
        except ValueError:
            pass

        print("Enter a whole number between 1 and 5000.")


def _print_readings(readings) -> None:
    print("\nSmart Meter Readings")
    print("Meter   Generated   Consumed   Net        Status")

    display_limit = 20
    for reading in readings[:display_limit]:
        if reading.net_kwh > 0:
            status = f"Sell {reading.net_kwh:.2f} kWh"
        elif reading.net_kwh < 0:
            status = f"Buy {abs(reading.net_kwh):.2f} kWh"
        else:
            status = "Balanced"

        print(
            f"{reading.meter_id:<7}"
            f"{reading.generated_kwh:>8.2f}   "
            f"{reading.consumed_kwh:>8.2f}   "
            f"{reading.net_kwh:>7.2f}   "
            f"{status}"
        )

    if len(readings) > display_limit:
        print(f"... {len(readings) - display_limit} more readings processed")


def _print_trades(trades) -> None:
    print("\nMarketplace Trades")

    if not trades:
        print("No buyer and seller could be matched.")
        return

    display_limit = 20
    for index, trade in enumerate(trades[:display_limit], start=1):
        print(
            f"{index:>2}. {trade.seller_meter_id} -> {trade.buyer_meter_id} | "
            f"{trade.quantity_kwh:.3f} kWh | "
            f"${trade.total_amount}"
        )

    if len(trades) > display_limit:
        print(f"... {len(trades) - display_limit} more trades created")


def _print_summary(metrics, marketplace, settlements) -> None:
    print("\nSystem Summary")
    print(f"Readings accepted: {metrics.readings_received}")
    print(f"Readings rejected: {metrics.readings_rejected}")
    print(f"Duplicate readings blocked: {metrics.duplicate_readings}")
    print(f"Events processed: {metrics.events_processed}")
    print(f"Trades created: {metrics.trades_created}")
    print(f"Settlements completed: {metrics.settlements_completed}")
    print(f"Unmatched supply: {marketplace.unmatched_supply_kwh:.3f} kWh")
    print(f"Unmatched demand: {marketplace.unmatched_demand_kwh:.3f} kWh")
    total = sum((record.amount for record in settlements.records), Decimal("0.00"))
    print(f"Total settlement value: ${total}")
    print(f"Ingestion throughput: {metrics.readings_per_second:.1f} readings/sec")


def _print_fitness(metrics) -> None:
    print("\nFitness Functions")

    for result in evaluate_fitness(metrics):
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.details}")


def run() -> None:
    print("EcoGrid Energy")
    print("Peer-to-peer renewable energy trading proof of concept\n")

    meter_count = _ask_meter_count()

    metrics = Metrics()
    event_bus = EventBus()
    ingestion = SmartMeterIngestion(event_bus, metrics)
    marketplace = Marketplace(event_bus, metrics)
    settlement = SettlementService(metrics)
    simulator = MeterSimulator()

    event_bus.subscribe("meter_reading_accepted", marketplace.handle_meter_event)
    event_bus.subscribe("trade_created", settlement.handle_trade_event)

    readings = simulator.create_batch(meter_count)

    for reading in readings:
        ingestion.ingest(reading)

    metrics.events_processed += event_bus.process_all()

    trades = marketplace.match_orders()

    metrics.events_processed += event_bus.process_all()

    _print_readings(readings)
    _print_trades(trades)
    _print_summary(metrics, marketplace, settlement)
    _print_fitness(metrics)

    print("\nSimulation complete.")
