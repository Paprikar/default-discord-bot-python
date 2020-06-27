from typing import Coroutine

from .discord_bot import DiscordBot


class DiscordEventHandler:
    bot: DiscordBot

    def __init__(self, bot: DiscordBot): ...

    def update_event(self, event: Coroutine): ...
