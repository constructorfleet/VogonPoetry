import structlog
import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
    )
    
def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)

logger = get_logger