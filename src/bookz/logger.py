import logging
import logging.config
import colorlog
import yaml
from pathlib import Path

def setup_logging():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    config_file = BASE_DIR / "config" / "logger.yaml"
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        print("Logger initialized successfully.")
    except FileNotFoundError:
        print(f"Error: Logging configuration file not found at {config_file}")
    except Exception as e:
        print(f"Error initializing logger: {e}")

setup_logging()

app_logger = logging.getLogger("app")
db_logger = logging.getLogger("db")

app_logger.info(f"App logger initialized: {app_logger.name}")
db_logger.info(f"DB logger initialized: {db_logger.name}")
