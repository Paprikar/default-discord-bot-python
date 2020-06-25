import sys

import discord

from .config import parse_config
from .discord_bot_attrs import DiscordBotAttrs
from .discord_event_handler import DiscordEventHandler
from .pics_manager import PicsManager


class DiscordBot(DiscordBotAttrs):

    def __init__(self, logger, formatter):
        self.client = discord.Client()
        self.logger = logger

        sys.excepthook = self._handle_unhandled_exception
        (
            self.token,
            self.command_prefix,
            self.bot_channel_id,
            self.pics_categories,
        ) = parse_config('config.json', logger, formatter)

        DiscordEventHandler(self)

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.critical('Unhandled exception:',
                             exc_info=(exc_type, exc_value, exc_traceback))

    def run(self):
        if self.pics_categories:
            for category in self.pics_categories.values():
                manager = PicsManager(self.client, category, self.logger)
                self.client.loop.create_task(manager.run())

        self.client.run(self.token)
