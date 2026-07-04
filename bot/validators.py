from dataclasses import dataclass
from typing import Optional, Union
 
Number = Union[str, float, int]
 
 
class ValidationError(Exception):
    """Raised when user-supplied order parameters fail validation."""
 
 
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"} 
VALID_SYMBOLS = {"BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"}
 
 
@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
 
 
def validate_symbol(symbol: str) -> str:
    if not symbol:
        raise ValidationError("Symbol is required.")
    symbol = symbol.strip().upper()
    if symbol not in VALID_SYMBOLS:
        raise ValidationError(
            f"Unsupported symbol '{symbol}'. Supported: {', '.join(sorted(VALID_SYMBOLS))}"
        )
    return symbol
 
 
def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("Order side is required.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Side must be one of {sorted(VALID_SIDES)}, got '{side}'.")
    return side
 
 
def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("Order type is required.")
    normalized = order_type.strip().upper().replace("-", "_").replace(" ", "_")
    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type must be one of {sorted(VALID_ORDER_TYPES)}, got '{order_type}'."
        )
    return normalized
 
 
def validate_quantity(quantity: Number) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    return quantity
 
 
def validate_price(price: Optional[Number], order_type: str) -> Optional[float]:
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price
    return None
 
 
def validate_stop_price(stop_price: Optional[Number], order_type: str) -> Optional[float]:
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_price <= 0:
            raise ValidationError("Stop price must be greater than zero.")
        return stop_price
    return None
 
 
def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Number,
    price: Optional[Number] = None,
    stop_price: Optional[Number] = None,
) -> OrderRequest:
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)
 
    return OrderRequest(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )