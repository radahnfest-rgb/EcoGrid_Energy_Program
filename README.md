# EcoGrid Energy Python Proof of Concept

This is a small console-based prototype for the EcoGrid Energy system design assessment.

It demonstrates three main responsibilities:

- Smart Meter Integration: generates and validates smart meter readings.
- Marketplace: separates sellers and buyers and matches available energy.
- Financial Settlement: creates a simple settlement record for each trade.

The components communicate through a small in-memory event bus so the smart meter ingestion logic is not directly coupled to settlement logic.

## Features

- Simulates smart meter generation and consumption readings.
- Identifies homes with surplus or deficit energy.
- Matches sellers with buyers.
- Creates settlement records using a fixed energy price.
- Rejects invalid meter readings.
- Prevents duplicate meter readings.
- Prevents duplicate settlement of the same trade.
- Tracks simple operational metrics.
- Runs measurable fitness-function checks.
- Includes unit tests.

## Project structure

```text
main.py
ecogrid/
    app.py
    event_bus.py
    fitness.py
    marketplace.py
    models.py
    observability.py
    settlement.py
    smart_meter.py
tests/
    test_ecogrid.py
```

## Requirements

Python 3.10 or newer.

No external packages are required.

## Run the program

From the project folder:

```bash
python main.py
```

Enter the number of smart meters to simulate, or press Enter to use 10.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Architecture idea demonstrated

The program keeps the three business areas separate.

Smart meter readings enter through `SmartMeterIngestion`. Valid readings are published as events. The `Marketplace` consumes those events and creates energy trades. Trade events are then handled by the `SettlementService`.

This is a small proof of concept rather than a production platform. A real implementation could replace the in-memory event bus with a message broker such as Kafka or RabbitMQ and replace the in-memory records with separate data stores.
