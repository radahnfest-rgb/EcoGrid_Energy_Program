import uuid
from decimal import Decimal

from .event_bus import EventBus
from .models import EnergyOrder, Trade
from .observability import Metrics


class Marketplace:
    def __init__(
        self,
        event_bus: EventBus,
        metrics: Metrics,
        price_per_kwh: Decimal = Decimal("0.30"),
    ) -> None:
        self.event_bus = event_bus
        self.metrics = metrics
        self.price_per_kwh = price_per_kwh
        self._sellers: list[EnergyOrder] = []
        self._buyers: list[EnergyOrder] = []

    def handle_meter_event(self, payload: dict) -> None:
        net_kwh = float(payload["net_kwh"])
        meter_id = payload["meter_id"]

        if net_kwh > 0:
            self._sellers.append(EnergyOrder(meter_id, round(net_kwh, 3)))
        elif net_kwh < 0:
            self._buyers.append(EnergyOrder(meter_id, round(abs(net_kwh), 3)))

    def match_orders(self) -> list[Trade]:
        trades: list[Trade] = []

        while self._sellers and self._buyers:
            seller = self._sellers[0]
            buyer = self._buyers[0]
            quantity = round(min(seller.quantity_kwh, buyer.quantity_kwh), 3)

            trade = Trade(
                trade_id=str(uuid.uuid4()),
                seller_meter_id=seller.meter_id,
                buyer_meter_id=buyer.meter_id,
                quantity_kwh=quantity,
                price_per_kwh=self.price_per_kwh,
            )
            trades.append(trade)
            self.metrics.trades_created += 1

            self.event_bus.publish(
                "trade_created",
                {
                    "trade": trade,
                },
            )

            seller.quantity_kwh = round(seller.quantity_kwh - quantity, 3)
            buyer.quantity_kwh = round(buyer.quantity_kwh - quantity, 3)

            if seller.quantity_kwh <= 0:
                self._sellers.pop(0)

            if buyer.quantity_kwh <= 0:
                self._buyers.pop(0)

        return trades

    @property
    def unmatched_supply_kwh(self) -> float:
        return round(sum(order.quantity_kwh for order in self._sellers), 3)

    @property
    def unmatched_demand_kwh(self) -> float:
        return round(sum(order.quantity_kwh for order in self._buyers), 3)
