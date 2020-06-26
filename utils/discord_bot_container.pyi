from logging import Logger

from discord import Client


class DiscordBotContainer:
    client: Client
    logger: Logger
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict

    def __init__(self): ...
