from logging import Formatter
from logging import Logger
from typing import Set
from typing import Tuple


def parse_config(config_path: str, logger: Logger, formatter: Formatter) -> Tuple[str, str, int, dict]: ...


def _check_category(category: dict, category_name: str, logger: Logger) -> Set[str]: ...


def _check_pics_sending_module(category: dict, category_name: str, logger: Logger) -> bool: ...


def _check_pics_suggestion_module(category: dict, category_name: str, logger: Logger) -> bool: ...


def _check_emoji(category: dict, category_name: str, key: str, default: str, logger: Logger): ...
