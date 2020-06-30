from typing import Coroutine

from .bot import DiscordBot


class DiscordBotEventHandler:
    bot: DiscordBot

    def __init__(self, bot: DiscordBot): ...

    def update_event(self, event: Coroutine): ...
