import asyncio
import sys

import discord

from .config import parse_config
from .discord_event_handler import DiscordEventHandler
from .pics_sending_manager import PicsSendingManager


class DiscordBot:

    def __init__(self, config_path, logger, formatter):
        self.config_path = config_path
        self.logger = logger
        self.formatter = formatter

        sys.excepthook = self._handle_unhandled_exception

        self._init()

    def _init(self):
        self.loop = asyncio.get_event_loop()
        self.client = discord.Client(loop=self.loop)
        (
            self.token,
            self.command_prefix,
            self.bot_channel_id,
            self.pics_categories,
        ) = parse_config(self.config_path, self.logger, self.formatter)

        self.shutdown_allowed = False
        self.event_handler = DiscordEventHandler(self)
        self.managers = []

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.critical(
            'Unhandled exception: ',
            exc_info=(exc_type, exc_value, exc_traceback))

    def run(self):
        while True:
            if self.pics_categories:
                for category_name in self.pics_categories:
                    manager = PicsSendingManager(category_name, self)
                    self.managers.append(manager)
                    manager.run()

            self.loop.create_task(self.client.start(self.token))

            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                self.shutdown('Shutting down.')
                break
            else:
                if self.shutdown_allowed:
                    break
                else:
                    self._init()

    def shutdown(self, msg):
        self.logger.info(msg)
        self.loop.create_task(self.close())
        self.loop.run_forever()
        self.loop.close()

    async def close(self):
        for manager in self.managers:
            await manager.close()
        await self.client.close()
        tasks = [t for t in asyncio.all_tasks()
                 if t is not asyncio.current_task()]
        await asyncio.gather(*tasks)
        self.loop.stop()
