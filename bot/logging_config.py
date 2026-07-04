import logging
import sys
from pathlib import Path
 
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"
 
 
def setup_logging(log_level: str = "INFO") -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
 
    level = getattr(logging, log_level.upper(), logging.INFO)
 
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
 
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
 
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
 
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
 
 
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
