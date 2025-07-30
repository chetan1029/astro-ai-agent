import logging
from logging.config import dictConfig
import json
from datetime import datetime
from app.src.core.config import get_settings
import os

APP_ENV = get_settings().app_env


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Capture extra fields
        if hasattr(record, "extra_info"):
            log_record["extra"] = record.extra_info

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


log_handlers = ["console"]
log_formatters = {
    "default": {"format": "%(levelname)s | %(asctime)s | %(name)s | %(message)s"}
}

if APP_ENV == "production":
    os.makedirs("logs", exist_ok=True)
    log_handlers.append("rotating_file")
    log_formatters["json"] = {"()": JsonFormatter}

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": log_formatters,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json" if APP_ENV == "production" else "default",
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/fastapi.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
        }
        if APP_ENV == "production"
        else None,
    },
    "loggers": {
        "app": {
            "handlers": log_handlers,
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}

# Clean up invalid handler (rotating_file in dev)
if APP_ENV != "production":
    log_config["handlers"].pop("rotating_file", None)

dictConfig(log_config)
logger = logging.getLogger("app")
