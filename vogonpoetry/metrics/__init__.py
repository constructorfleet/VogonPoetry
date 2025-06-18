"""Metrics configuration module."""

from pymetrics.recorders.default import DefaultMetricsRecorder
from pymetrics.instruments import Counter, Gauge, Histogram, Timer, TimerResolution


class MetricsCollection(DefaultMetricsRecorder):
    """Metrics collection configuration."""

    def __init__(self):
        super().__init__(
            "vogonpoetry",
            config={
                "version": 2,
                "publishers": [
                    {
                        "path": "vogonpoetry.metrics.logger.LoggerPublisher",
                        "kwargs": {
                            "log_name": "vogonpoetry.metrics",
                            "log_level": "INFO",
                        },
                    }
                ],
            },
        )

    def increment(self, name: str, **tags):
        """Get or create a counter metric."""
        self.counter(name, **tags).increment(1)

    def time(self, name: str, **tags) -> Timer:
        """Get or create a gauge metric."""
        return self.timer(name,resolution=TimerResolution.NANOSECONDS, **tags)
