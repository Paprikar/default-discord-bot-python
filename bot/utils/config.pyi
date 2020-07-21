from logging import Formatter
from logging import Logger
from typing import Dict
from typing import Optional
from typing import Set


class Config:
    token: str
    command_prefix: str
    bot_channel_id: int
    db: Optional[Dict]
    reconnect_timeout: float
    pics_categories: Optional[Dict]

    def __init__(self, config_path: str, logger: Logger, formatter: Formatter): ...

    def _parse_config(self): ...

    def _check_db(self, db: Dict) -> Dict: ...

    def _check_pics_category(self, category: Dict, category_name: str) -> Set[str]: ...

    def _check_pics_sending_module(self, category: Dict, category_name: str) -> bool: ...

    def _check_pics_suggestion_module(self, category: Dict, category_name: str) -> bool: ...

    def _check_emoji(self, category: Dict, category_name: str, key: str, default: str): ...
