from asyncio import Event
from asyncio import Task
from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple

from bot.bot import DiscordBot
from .module import Module


class PicsSendingModule(Module):
    tasks: Dict[Task, Optional[Event]]
    monitoring_events: Dict[str, Event]
    last_send_datetime: Dict[str, Optional[datetime]]

    def __init__(self, bot: DiscordBot): ...

    async def _start(self, category_name: str): ...

    async def _start_monitoring(self, category_name: str, refresh_time: float = 60): ...

    @staticmethod
    async def _time_check(category_name: str) -> Tuple[bool, float]: ...

    def _get_last_send_datetime_db(self, category_name: str) -> Optional[datetime]: ...

    def _set_last_send_datetime_db(self, category_name: str, datetime: Optional[datetime]): ...

    async def _send_pic(self, category_name: str) -> bool: ...

    @staticmethod
    def _select_pic(pics: Sequence[str]): ...

    async def _close(self, timeout: Optional[float] = None): ...

    async def _closer(self): ...

    async def _task_closer(self, task: Task): ...
