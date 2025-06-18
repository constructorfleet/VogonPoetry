from types import TracebackType
from typing import Mapping
import structlog
import logging


class StructLogger(logging.Logger):
    def __init__(self, name: str, level: int | str = 0) -> None:
        super().__init__(name, level)
        self._logger = get_logger(name)

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.info(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.error(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.debug(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def warn(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.warn(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.warn(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def trace(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.trace(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def fatal(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.fatal(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        return self._logger.critical(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            **(extra or {}),
        )

    def log(self, level: int, msg: object, *args: object, **kwargs) -> None:
        return self._logger.log(level, msg, *args, **kwargs)


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
    )
    logging.setLoggerClass(StructLogger)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)


logger = get_logger
