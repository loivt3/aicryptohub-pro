"""
Structured logging configuration for AI Hub AI Engine
Outputs JSON logs for easy parsing by ELK stack
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON log formatter for ELK stack"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class StructuredLogger(logging.Logger):
    """Logger with structured logging support"""
    
    def _log_with_extra(self, level: int, msg: str, extra: Dict[str, Any] = None, **kwargs):
        if extra:
            # Attach extra to record
            old_factory = logging.getLogRecordFactory()
            
            def factory(*args, **kw):
                record = old_factory(*args, **kw)
                record.extra = extra
                return record
            
            logging.setLogRecordFactory(factory)
            super()._log(level, msg, (), **kwargs)
            logging.setLogRecordFactory(old_factory)
        else:
            super()._log(level, msg, (), **kwargs)
    
    def info_with_context(self, msg: str, **context):
        self._log_with_extra(logging.INFO, msg, context)
    
    def error_with_context(self, msg: str, **context):
        self._log_with_extra(logging.ERROR, msg, context)


def configure_logging(json_output: bool = True, level: str = "INFO") -> None:
    """
    Configure application logging
    
    Args:
        json_output: If True, use JSON format (for ELK). If False, use standard format.
        level: Logging level
    """
    # Set custom logger class
    logging.setLoggerClass(StructuredLogger)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
    
    root_logger.addHandler(console_handler)
    
    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info("Logging configured", extra={"json_output": json_output, "level": level})


# Convenience loggers for different components
def get_component_logger(component: str) -> logging.Logger:
    """Get logger for a specific component"""
    return logging.getLogger(f"aihub.{component}")


# Pre-configured component loggers
api_logger = get_component_logger("api")
db_logger = get_component_logger("database")
analysis_logger = get_component_logger("analysis")
cache_logger = get_component_logger("cache")
gemini_logger = get_component_logger("gemini")
