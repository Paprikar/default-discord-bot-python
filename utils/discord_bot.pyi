from logging import Formatter
from logging import Logger

from discord import Client

from .discord_event_handler import DiscordEventHandler


class DiscordBot:
    config_path: str
    logger: Logger
    formatter: Formatter
    client: Client
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict
    shutdown_allowed: bool = False
    event_handler: DiscordEventHandler

    def __init__(self, config_path: str, logger: Logger, formatter: Formatter): ...

    def run(self): ...

    async def close(self): ...
