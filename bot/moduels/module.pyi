from asyncio import Lock
from asyncio import Task
from typing import Optional

from bot.bot import DiscordBot


class Module:
    bot: DiscordBot
    to_close: Lock
    close_task: Task

    def run(self): ...

    def stop(self, timeout: Optional[float] = None): ...
