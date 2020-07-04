from asyncio import Event
from asyncio import Task
from typing import Dict
from typing import Optional
from typing import Sequence

from .module import Module
from ..bot import DiscordBot


class PicsSendingModule(Module):
    tasks: Dict[Task, Event]

    def __init__(self, bot: DiscordBot): ...

    async def start(self, category_name: str): ...

    async def close(self, timeout: Optional[float] = None): ...

    async def _closer(self): ...

    async def _task_closer(self, task: Task): ...

    @staticmethod
    def _time_check(send_time: Sequence[str]): ...

    async def _send_pic(self, channel_id: int, directory: str): ...

    @staticmethod
    def _select_pic(pics: Sequence[str]): ...
