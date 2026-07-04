import argparse
import sys
 
from dotenv import load_dotenv
load_dotenv()
 
from bot.client import BinanceFuturesTestnetClient, BinanceClientError
from bot.logging_config import setup_logging, get_logger
from bot.orders import place_order, summarize_request, summarize_response, OrderExecutionError
from bot.validators import build_order_request, ValidationError
 
logger = get_logger(__name__)
 
 
def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place MARKET, LIMIT, or STOP_LIMIT orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        help="MARKET, LIMIT, or STOP_LIMIT (aliases: STOP-LIMIT, 'STOP LIMIT')",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", default=None, help="Required for LIMIT and STOP_LIMIT")
    parser.add_argument(
        "--stop-price", dest="stop_price", default=None, help="Required for STOP_LIMIT"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log verbosity (the file log always captures DEBUG and above)",
    )
    return parser.parse_args(argv)
 
 
def main(argv=None) -> int:
    args = parse_args(argv)
    setup_logging(log_level=args.log_level)
 
    # 1. Validate input
    try:
        order = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n✗ Invalid input: {exc}\n")
        return 1
 
    print("\n" + summarize_request(order) + "\n")
    logger.info("Validated order request: %s", order)
 
    # 2. Connect to Binance Futures Testnet
    try:
        client = BinanceFuturesTestnetClient()
        client.ping()
    except BinanceClientError as exc:
        logger.error("Connection failed: %s", exc)
        print(f"\n✗ Could not connect to Binance Futures Testnet: {exc}\n")
        return 1
 
    # 3. Place the order
    try:
        response = place_order(client, order)
    except OrderExecutionError as exc:
        print(f"\n✗ Order failed: {exc}\n")
        return 1
    except Exception as exc:
        logger.exception("Unexpected error while placing order")
        print(f"\n✗ Unexpected error: {exc}\n")
        return 1
 
    # 4. Report result
    print("\n" + summarize_response(response) + "\n")
    print("✓ Order placed successfully.\n")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
