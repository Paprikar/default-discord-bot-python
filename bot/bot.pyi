from asyncio import AbstractEventLoop
from logging import Formatter
from logging import Logger
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from discord import Client

from .bot_event_handler import DiscordBotEventHandler
from .moduels import Module


T_Module = TypeVar('T_Module', bound=Module)


class DiscordBot:
    config_path: str
    logger: Logger
    formatter: Formatter
    loop: AbstractEventLoop
    client: Client
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict
    shutdown_allowed: bool = False
    event_handler: DiscordBotEventHandler
    modules: List[Type[Module]]

    def __init__(self, config_path: str, logger: Logger, formatter: Formatter): ...

    def run(self): ...

    def stop(self, msg: Optional[str] = None, timeout: Optional[float] = None): ...

    async def close(self, timeout: Optional[float] = None): ...

    def get_module(self, module_type: Type[T_Module]) -> Optional[T_Module]: ...
