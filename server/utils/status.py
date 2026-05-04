"""FastInOut 全局状态枚举 — v3.0 所有模块统一使用"""


class SalesOrderStatus:
    DRAFT = "draft"
    PENDING = "pending"
    AUDITED = "audited"
    CONVERTED = "converted"
    LOCKED = "locked"


class SalesDeliveryStatus:
    PENDING = "pending"
    SETTLING = "settling"
    SETTLED = "settled"
    VOIDED = "voided"
    LOCKED = "locked"
    REVERSED = "reversed"


class PurchaseReceiptStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REVERSED = "reversed"


class ReturnDeliveryStatus:
    PENDING = "pending"
    WAREHOUSE_CONFIRMED = "warehouse_confirmed"
    FINANCE_CONFIRMED = "finance_confirmed"
    SETTLED = "settled"


class SettlementStatus:
    PENDING = "pending"
    AUDITED = "audited"
    REJECTED = "rejected"


class StocktakingStatus:
    DRAFT = "draft"
    PENDING = "pending"
    AUDITING = "auditing"
    AUDITED = "audited"
    ADJUSTED = "adjusted"


class VehicleLoadStatus:
    DRAFT = "draft"
    PENDING = "pending"
    LOADED = "loaded"
    PARTIAL_RETURN = "partial_return"
    RETURNED = "returned"
