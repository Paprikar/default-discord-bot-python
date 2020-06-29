from .module import Module
from ..bot import DiscordBot


class PicsSendingModule(Module):

    def __init__(self, category_name: str, bot: DiscordBot): ...
