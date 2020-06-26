import sys

import discord

from .config import parse_config
from .discord_bot_container import DiscordBotContainer
from .discord_event_handler import DiscordEventHandler
from .pics_manager import PicsManager


class DiscordBot:

    def __init__(self, config_path, logger, formatter):
        self.container = DiscordBotContainer()
        self.container.client = discord.Client()
        self.container.logger = logger

        sys.excepthook = self._handle_unhandled_exception
        (
            self.container.token,
            self.container.command_prefix,
            self.container.bot_channel_id,
            self.container.pics_categories,
        ) = parse_config(config_path, logger, formatter)

        self.event_handler = DiscordEventHandler(self.container)

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.container.logger.critical(
            'Unhandled exception: ',
            exc_info=(exc_type, exc_value, exc_traceback))

    def run(self):
        if self.container.pics_categories:
            for category_name in self.container.pics_categories:
                manager = PicsManager(category_name, self.container)
                self.container.client.loop.create_task(manager.run())

        self.container.client.run(self.container.token)
