import sys
from typing import Optional
 
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
 
from dotenv import load_dotenv
 
load_dotenv()
 
from bot.client import BinanceClientError, BinanceFuturesTestnetClient
from bot.logging_config import get_logger, setup_logging
from bot.orders import OrderExecutionError, place_order
from bot.validators import (
    VALID_ORDER_TYPES,
    VALID_SIDES,
    VALID_SYMBOLS,
    OrderRequest,
    ValidationError,
    build_order_request,
)
 
app = typer.Typer(add_completion=False, help="PrimeTrade.ai Trading Bot -- interactive CLI")
console = Console()
logger = get_logger("cli_rich")
 
 
def _prompt_for_missing(
    symbol: Optional[str],
    side: Optional[str],
    order_type: Optional[str],
    quantity: Optional[str],
    price: Optional[str],
    stop_price: Optional[str],
):
    
    if not any([symbol, side, order_type, quantity, price, stop_price]):
        console.print(
            Panel.fit(
                "[bold cyan]PrimeTrade.ai Trading Bot[/bold cyan]\n"
                "Binance Futures Testnet (USDT-M)",
                border_style="cyan",
            )
        )
 
    if not symbol:
        symbol = Prompt.ask("Symbol", choices=sorted(VALID_SYMBOLS), default="BTCUSDT")
    if not side:
        side = Prompt.ask("Side", choices=sorted(VALID_SIDES))
    if not order_type:
        order_type = Prompt.ask("Order type", choices=sorted(VALID_ORDER_TYPES), default="MARKET")
 
    normalized_type = order_type.strip().upper().replace("-", "_").replace(" ", "_")
 
    if quantity is None:
        quantity = Prompt.ask("Quantity")
    if normalized_type in ("LIMIT", "STOP_LIMIT") and price is None:
        price = Prompt.ask("Price")
    if normalized_type == "STOP_LIMIT" and stop_price is None:
        stop_price = Prompt.ask("Stop price (trigger)")
 
    return symbol, side, order_type, quantity, price, stop_price
 
 
def _render_summary(order: OrderRequest) -> Table:
    table = Table(title="Order Request Summary", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Symbol", order.symbol)
    table.add_row("Side", order.side)
    table.add_row("Type", order.order_type)
    table.add_row("Quantity", str(order.quantity))
    if order.price is not None:
        table.add_row("Price", str(order.price))
    if order.stop_price is not None:
        table.add_row("Stop Price", str(order.stop_price))
    return table
 
 
def _render_response(response: dict) -> Table:
    is_algo_order = "algoId" in response
    table = Table(title="Order Response", show_header=False, border_style="green")
    table.add_column("Field", style="bold")
    table.add_column("Value")
 
    if is_algo_order:
        table.add_row("Algo ID", str(response.get("algoId", "N/A")))
        table.add_row("Status", f"{response.get('algoStatus', 'N/A')} (resting until triggered)")
        table.add_row("Trigger Price", str(response.get("triggerPrice", "N/A")))
    else:
        table.add_row("Order ID", str(response.get("orderId", "N/A")))
        table.add_row("Status", str(response.get("status", "N/A")))
        table.add_row("Executed Qty", str(response.get("executedQty", "N/A")))
        if response.get("avgPrice") is not None:
            table.add_row("Avg Price", str(response.get("avgPrice")))
    return table
 
 
@app.command()
def place(
    symbol: Optional[str] = typer.Option(None, "--symbol", help="e.g. BTCUSDT"),
    side: Optional[str] = typer.Option(None, "--side", help="BUY or SELL"),
    order_type: Optional[str] = typer.Option(None, "--type", help="MARKET, LIMIT, or STOP_LIMIT"),
    quantity: Optional[str] = typer.Option(None, "--quantity", help="Order quantity"),
    price: Optional[str] = typer.Option(None, "--price", help="Required for LIMIT / STOP_LIMIT"),
    stop_price: Optional[str] = typer.Option(
        None, "--stop-price", help="Required for STOP_LIMIT"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt"),
    log_level: str = typer.Option("INFO", "--log-level", help="Console log verbosity"),
):
    setup_logging(log_level=log_level)
    interactive = sys.stdin.isatty()
 
    symbol, side, order_type, quantity, price, stop_price = _prompt_for_missing(
        symbol, side, order_type, quantity, price, stop_price
    )
 
    while True:
        try:
            order = build_order_request(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
            )
            break
        except ValidationError as exc:
            console.print(Panel(str(exc), title="Invalid Input", border_style="red"))
            if not interactive:
                raise typer.Exit(code=1)
            symbol, side, order_type, quantity, price, stop_price = _prompt_for_missing(
                None, None, None, None, None, None
            )
 
    console.print(_render_summary(order))
    logger.info("Validated order request: %s", order)
 
    if not yes:
        if not Confirm.ask("Submit this order to Binance Futures Testnet?"):
            console.print("[yellow]Cancelled -- no order was sent.[/yellow]")
            raise typer.Exit(code=0)
 
    try:
        client = BinanceFuturesTestnetClient()
        client.ping()
    except BinanceClientError as exc:
        console.print(Panel(str(exc), title="Connection Failed", border_style="red"))
        raise typer.Exit(code=1)
 
    try:
        response = place_order(client, order)
    except OrderExecutionError as exc:
        console.print(Panel(str(exc), title="Order Failed", border_style="red"))
        raise typer.Exit(code=1)
    except Exception as exc:
        logger.exception("Unexpected error while placing order")
        console.print(Panel(str(exc), title="Unexpected Error", border_style="red"))
        raise typer.Exit(code=1)
 
    console.print(_render_response(response))
    console.print("[bold green]✓ Order placed successfully.[/bold green]")
 
 
if __name__ == "__main__":
    app()