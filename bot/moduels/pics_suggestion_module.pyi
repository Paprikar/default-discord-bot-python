from aiohttp.web import Server
from aiohttp.web import ServerRunner
from aiohttp.web import TCPSite
from discord import RawReactionActionEvent

from .module import Module
from ..bot import DiscordBot


class PicsSuggestionModule(Module):
    suggestion_info: dict
    server: Server
    server_runner: ServerRunner
    site: TCPSite

    def __init__(self, bot: DiscordBot): ...

    async def reaction_handler(self, payload: RawReactionActionEvent): ...
