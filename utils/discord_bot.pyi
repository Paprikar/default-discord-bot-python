from logging import Formatter
from logging import Logger

from .discord_bot_attrs import DiscordBotAttrs


class DiscordBot(DiscordBotAttrs):

    def __init__(self, logger: Logger, formatter: Formatter): pass

    def run(self): pass
