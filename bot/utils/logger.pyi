from logging import Formatter
from logging import Logger


def init_logger(name: str, formatter: Formatter) -> Logger:
    """Initiates a logger.

    A logger is created that uses console and file output handlers.
    The format "%Y-%m-%d-%H-%M-%S" is applied to the datetime part.
    File output handler writes to the file at path ``name + '.log'``.

    Args:
        name: The name of the logger.
        formatter: Formatter's object.

    Returns:
        An initialized logger object.

    """
