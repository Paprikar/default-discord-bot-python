from asyncio import AbstractEventLoop
from logging import Formatter
from logging import Logger
from typing import List
from typing import Type

from discord import Client

from .discord_event_handler import DiscordEventHandler
from .manager import Manager


class DiscordBot:
    config_path: str
    logger: Logger
    formatter: Formatter
    loop: AbstractEventLoop
    client: Client
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict
    shutdown_allowed: bool = False
    event_handler: DiscordEventHandler
    managers: List[Type[Manager]]

    def __init__(self, config_path: str, logger: Logger, formatter: Formatter): ...

    def run(self): ...

    def shutdown(self, msg: str): ...

    async def close(self): ...
