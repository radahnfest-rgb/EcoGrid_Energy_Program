from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class ParticipantRole(str, Enum):
    SELLER = "Seller"
    BUYER = "Buyer"
    BALANCED = "Balanced"


@dataclass(frozen=True)
class MeterReading:
    reading_id: str
    meter_id: str
    generated_kwh: float
    consumed_kwh: float
    timestamp: float

    @property
    def net_kwh(self) -> float:
        return round(self.generated_kwh - self.consumed_kwh, 3)

    @property
    def role(self) -> ParticipantRole:
        if self.net_kwh > 0:
            return ParticipantRole.SELLER
        if self.net_kwh < 0:
            return ParticipantRole.BUYER
        return ParticipantRole.BALANCED


@dataclass
class EnergyOrder:
    meter_id: str
    quantity_kwh: float


@dataclass(frozen=True)
class Trade:
    trade_id: str
    seller_meter_id: str
    buyer_meter_id: str
    quantity_kwh: float
    price_per_kwh: Decimal

    @property
    def total_amount(self) -> Decimal:
        amount = Decimal(str(self.quantity_kwh)) * self.price_per_kwh
        return amount.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class SettlementRecord:
    trade_id: str
    amount: Decimal
    status: str
