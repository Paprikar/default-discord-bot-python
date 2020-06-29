from .discord_bot import DiscordBot
from .manager import Manager


class PicsSuggestionManager(Manager):

    def __init__(self, category_name: str, bot: DiscordBot): ...
