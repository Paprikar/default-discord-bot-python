import logging
from typing import Optional, Sequence, Type

import discord


class DiscordBotAttrs:
    client: discord.Client
    logger: logging.Logger
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict

    @staticmethod
    def fill_attrs(source: Type[DiscordBotAttrs], target: Type[DiscordBotAttrs], names: Optional[Sequence[str]] = None): pass
