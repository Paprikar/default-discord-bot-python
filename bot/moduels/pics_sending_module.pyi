from asyncio import Event
from asyncio import Task
from typing import Dict
from typing import Optional

from .module import Module
from ..bot import DiscordBot


class PicsSendingModule(Module):
    tasks: Dict[Task, Event]

    def __init__(self, bot: DiscordBot): ...

    async def start(self, category_name: str): ...

    async def close(self, timeout: Optional[float] = None): ...
