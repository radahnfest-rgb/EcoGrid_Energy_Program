from .models import SettlementRecord, Trade
from .observability import Metrics


class SettlementService:
    def __init__(self, metrics: Metrics) -> None:
        self.metrics = metrics
        self._settled_trade_ids = set()
        self.records: list[SettlementRecord] = []

    def handle_trade_event(self, payload: dict) -> None:
        trade: Trade = payload["trade"]
        self.settle(trade)

    def settle(self, trade: Trade) -> SettlementRecord | None:
        # This prevents the same trade from being charged twice.
        if trade.trade_id in self._settled_trade_ids:
            self.metrics.settlement_duplicates_prevented += 1
            return None

        record = SettlementRecord(
            trade_id=trade.trade_id,
            amount=trade.total_amount,
            status="COMPLETED",
        )

        self._settled_trade_ids.add(trade.trade_id)
        self.records.append(record)
        self.metrics.settlements_completed += 1
        return record
