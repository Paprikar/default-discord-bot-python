from .module import Module
from ..bot import DiscordBot


class PicsSendingModule(Module):

    def __init__(self, bot: DiscordBot, category_name: str): ...
