from bot.client import BinanceFuturesTestnetClient, BinanceClientError
from bot.logging_config import get_logger
from bot.validators import OrderRequest
 
logger = get_logger(__name__)
 
 
class OrderExecutionError(Exception):
    """Raised when an order cannot be placed, wrapping the underlying cause."""
 
 
def _build_binance_params(order: OrderRequest) -> dict:
    params = {
        "symbol": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
    }
 
    if order.order_type == "MARKET":
        params["type"] = "MARKET"
 
    elif order.order_type == "LIMIT":
        params.update(
            {
                "type": "LIMIT",
                "price": order.price,
                "timeInForce": "GTC",
            }
        )
 
    elif order.order_type == "STOP_LIMIT":
        params.update(
            {
                "type": "STOP",
                "price": order.price,
                "stopPrice": order.stop_price,
                "timeInForce": "GTC",
            }
        )
    else:
        raise OrderExecutionError(f"Unsupported order type: {order.order_type}")
 
    return params
 
 
def place_order(client: BinanceFuturesTestnetClient, order: OrderRequest) -> dict:
    params = _build_binance_params(order)
 
    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
        order.side,
        order.order_type,
        order.symbol,
        order.quantity,
        order.price,
        order.stop_price,
    )
 
    try:
        response = client.place_order(**params)
    except BinanceClientError as exc:
        logger.error("Order failed: %s", exc)
        raise OrderExecutionError(str(exc)) from exc
    order_id = response.get("orderId", response.get("algoId"))
    order_status = response.get("status", response.get("algoStatus"))
    logger.info("Order accepted | id=%s status=%s", order_id, order_status)
    return response
 
 
def summarize_request(order: OrderRequest) -> str:
    lines = [
        "Order Request Summary",
        "----------------------",
        f"Symbol:      {order.symbol}",
        f"Side:        {order.side}",
        f"Type:        {order.order_type}",
        f"Quantity:    {order.quantity}",
    ]
    if order.price is not None:
        lines.append(f"Price:       {order.price}")
    if order.stop_price is not None:
        lines.append(f"Stop Price:  {order.stop_price}")
    return "\n".join(lines)
 
 
def summarize_response(response: dict) -> str:
    is_algo_order = "algoId" in response
 
    lines = ["Order Response", "----------------------"]
 
    if is_algo_order:
        lines.append(f"Algo ID:       {response.get('algoId', 'N/A')}")
        lines.append(f"Status:        {response.get('algoStatus', 'N/A')} (resting until triggered)")
        lines.append(f"Trigger Price: {response.get('triggerPrice', 'N/A')}")
    else:
        lines.append(f"Order ID:      {response.get('orderId', 'N/A')}")
        lines.append(f"Status:        {response.get('status', 'N/A')}")
        lines.append(f"Executed Qty:  {response.get('executedQty', 'N/A')}")
        avg_price = response.get("avgPrice")
        if avg_price is not None:
            lines.append(f"Avg Price:     {avg_price}")
 
    return "\n".join(lines)
