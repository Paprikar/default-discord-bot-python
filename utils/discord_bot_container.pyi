from logging import Logger

from discord import Client

from .discord_bot import DiscordBot


class DiscordBotContainer:
    client: Client
    logger: Logger
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict
    discord_bot: DiscordBot
    shutdown_allowed: bool = False

    def __init__(self): ...
