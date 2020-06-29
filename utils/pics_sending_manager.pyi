from .discord_bot import DiscordBot
from .manager import Manager


class PicsSendingManager(Manager):

    def __init__(self, category_name: str, bot: DiscordBot): ...
