import logging
import six
from pymetrics.publishers.logging import LogPublisher

from vogonpoetry.logging import logger

def metric_key(metric) -> str:
    return f"{metric.name}{{{','.join(f'{k}={v}' for k, v in sorted(metric.tags.items()))}}}"

class LoggerPublisher(LogPublisher):
    def __init__(self, log_name: str, *args, log_level: int | str = logging.INFO, **kwargs):
        super().__init__(log_name, *args, log_level=log_level, **kwargs)
        self._logger = logger(log_name)

    def publish(self, metrics, error_logger=None, enable_meta_metrics=False) -> None:
        self._logger.log(self.log_level, "Metrics", **{metric_key(m): six.text_type(m.value) for m in metrics})