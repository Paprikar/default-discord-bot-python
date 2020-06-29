from asyncio import Event
from asyncio import Lock
from asyncio import Task

from ..bot import DiscordBot


class Module:
    bot: DiscordBot
    task: Task
    closable: Event
    to_close: Lock

    def run(self): ...

    async def start(self): ...

    async def close(self): ...
