from asyncio import Lock
from asyncio import Task
from typing import List
from typing import Optional

from ..bot import DiscordBot


class Module:
    bot: DiscordBot
    to_close: Lock
    close_task: Task

    def run(self): ...

    async def start(self, *args, **kwargs): ...

    def stop(self, timeout: Optional[float] = None): ...

    async def close(self, *args, **kwargs): ...
