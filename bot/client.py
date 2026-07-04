import os
from typing import Optional
 
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
 
from bot.logging_config import get_logger
 
logger = get_logger(__name__)
 
FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"

NETWORK_EXCEPTIONS = (BinanceAPIException, BinanceRequestException, requests.exceptions.RequestException)
 
 
class BinanceClientError(Exception):
    """Raised when the Binance API returns an error or the request fails outright."""
 
 
class BinanceFuturesTestnetClient: 
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        api_key = api_key or os.getenv("BINANCE_API_KEY")
        api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
 
        if not api_key or not api_secret:
            raise BinanceClientError(
                "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET "
                "as environment variables, or in a .env file (see README)."
            )
 
        self.client = Client(api_key, api_secret, testnet=True, ping=False)
        self.client.FUTURES_URL = FUTURES_TESTNET_URL + "/fapi"
 
        logger.info("BinanceFuturesTestnetClient initialized against %s", FUTURES_TESTNET_URL)
 
    def ping(self) -> bool:
        try:
            self.client.futures_ping()
            logger.info("Ping successful. Testnet reachable.")
            return True
        except NETWORK_EXCEPTIONS as exc:
            logger.error("Ping failed: %s", exc)
            raise BinanceClientError(f"Could not reach Binance Futures Testnet: {exc}") from exc
 
    def get_server_time(self) -> int:
        try:
            return self.client.futures_time()["serverTime"]
        except NETWORK_EXCEPTIONS as exc:
            logger.error("Failed to fetch server time: %s", exc)
            raise BinanceClientError(str(exc)) from exc
 
    def place_order(self, **params) -> dict:
        logger.info("Sending order request: %s", params)
        try:
            response = self.client.futures_create_order(**params)
            logger.info("Order response received: %s", response)
            return response
        except NETWORK_EXCEPTIONS as exc:
            logger.error("Order placement failed: %s", exc)
            raise BinanceClientError(str(exc)) from exc
 
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        try:
            if symbol:
                return self.client.futures_get_open_orders(symbol=symbol)
            return self.client.futures_get_open_orders()
        except NETWORK_EXCEPTIONS as exc:
            logger.error("Failed to fetch open orders: %s", exc)
            raise BinanceClientError(str(exc)) from exc
 
    def cancel_order(self, symbol: str, order_id) -> dict:
        logger.info("Cancelling order %s (%s)", order_id, symbol)
        try:
            response = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info("Cancel response: %s", response)
            return response
        except NETWORK_EXCEPTIONS as exc:
            logger.error("Cancel failed: %s", exc)
            raise BinanceClientError(str(exc)) from exc
