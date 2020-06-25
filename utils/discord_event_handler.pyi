from typing import Coroutine

from .discord_bot import DiscordBot
from .discord_bot_attrs import DiscordBotAttrs


class DiscordEventHandler(DiscordBotAttrs):

    def __init__(self, discord_bot: DiscordBot): pass

    def update_event(self, event: Coroutine): pass
