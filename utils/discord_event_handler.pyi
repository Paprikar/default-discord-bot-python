from typing import Coroutine

from .discord_bot_container import DiscordBotContainer


class DiscordEventHandler:

    def __init__(self, container: DiscordBotContainer): ...

    def update_event(self, event: Coroutine): ...
