from logging import Formatter
from logging import Logger
from typing import Dict
from typing import Optional
from typing import Set


class Config:
    """Class to parse the configuration for the bot.

    Attributes:
        token: Bot's token.
        command_prefix: The string from which the message should begin
            for the bot to react in a special discord text channel.
        bot_channel_id: The discord text channel id
            in which the bot reacts to commands.
        db: Database configuration parameters.
        reconnect_timeout: The amount of time in seconds between attempts
            to reconnect at the start of the bot.
        pics_categories: The parameters responsible
            for configuring image categories.

    Raises:
        TypeError: Type error on reading data from configuration file.
        ValueError: Error of data value when reading them
            from the configuration file.
        ModuleNotFoundError: The configuration tries to use a module
            that is not found.
        psycopg2.DatabaseError: Error caused by a test connection attempt
            to the database.
        AssertionError: Error caused by checking configuration parameters.

    """

    token: str
    command_prefix: str
    bot_channel_id: int
    db: Optional[Dict]
    reconnect_timeout: float
    pics_categories: Optional[Dict]

    def __init__(self, config_path: str, logger: Logger, formatter: Formatter):
        """
        Args:
            config_path: The path to the json configuration file.
            logger: Logger's object.
            formatter: Formatter's object.

        """

    def _parse_config(self): ...

    def _check_db(self, db: Dict) -> Dict: ...

    def _check_pics_category(self, category: Dict, category_name: str) -> Set[str]: ...

    def _check_pics_sending_module(self, category: Dict, category_name: str) -> bool: ...

    def _check_pics_suggestion_module(self, category: Dict, category_name: str) -> bool: ...

    def _check_emoji(self, category: Dict, category_name: str, key: str, default: str): ...
