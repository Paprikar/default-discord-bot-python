import sys

import discord

from .config import parse_config
from .discord_event_handler import DiscordEventHandler
from .pics_manager import PicsManager


class DiscordBot:

    def __init__(self, config_path, logger, formatter):
        self.config_path = config_path
        self.logger = logger
        self.formatter = formatter

        sys.excepthook = self._handle_unhandled_exception

        self._init()

    def _init(self):
        self.client = discord.Client()
        (
            self.token,
            self.command_prefix,
            self.bot_channel_id,
            self.pics_categories,
        ) = parse_config(self.config_path, self.logger, self.formatter)

        self.shutdown_allowed = False
        self.event_handler = DiscordEventHandler(self)

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.critical(
            'Unhandled exception: ',
            exc_info=(exc_type, exc_value, exc_traceback))

    async def _runner(self):
        try:
            await self.client.start(self.token)
        finally:
            await self.close()

    def _stop_loop_on_completion(self, f):
        self.client.loop.stop()

    def _shutdown(self, msg, task_stop):
        task_stop.remove_done_callback(self._stop_loop_on_completion)
        self.logger.info(msg)
        self.client.loop.run_until_complete(
            self.client.close())

    def run(self):
        loop = self.client.loop
        while True:
            if self.pics_categories:
                for category_name in self.pics_categories:
                    manager = PicsManager(category_name, self)
                    loop.create_task(manager.run())

            task_stop = loop.create_task(self._runner())
            task_stop.add_done_callback(self._stop_loop_on_completion)

            try:
                loop.run_forever()
            except KeyboardInterrupt:
                self._shutdown('Shutdown.', task_stop)
                break
            else:
                if self.shutdown_allowed:
                    self._shutdown('Shutdown.', task_stop)
                    break
                else:
                    self._shutdown('Restart...', task_stop)
                    self._init()

    async def close(self):
        await self.client.close()
