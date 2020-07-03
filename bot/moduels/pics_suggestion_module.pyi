from typing import Dict
from typing import Optional
from typing import Tuple

from aiohttp.web import Server
from aiohttp.web import ServerRunner
from aiohttp.web import TCPSite
from discord import RawReactionActionEvent

from .module import Module
from ..bot import DiscordBot


class PicsSuggestionModule(Module):
    suggestion_info: Dict[int, Tuple[str, str, str]]
    server: Server
    server_runner: ServerRunner
    site: TCPSite

    def __init__(self, bot: DiscordBot): ...

    async def start(self): ...

    async def close(self, timeout: Optional[float] = None): ...

    async def reaction_handler(self, payload: RawReactionActionEvent): ...
