import asyncio
import sys

import discord

from .bot_event_handler import DiscordBotEventHandler
from .moduels import PicsSendingModule
from .moduels import PicsSuggestionModule
from .utils import parse_config


class DiscordBot:

    def __init__(self, config_path, logger, formatter):
        self._log_prefix = f'{type(self).__name__}: '

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
        self.event_handler = DiscordBotEventHandler(self)
        self.modules = []

        msg = 'Activated modules:\n'
        if self.pics_categories:
            msg += '  Pics categories:\n'
            for k in self.pics_categories:
                msg += f'    {k}:\n'
                for module in self.pics_categories[k]['modules']:
                    msg += f'      {module}\n'
            self.logger.info(self._log_prefix + msg.rstrip())

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error(
            self._log_prefix +
            'Unhandled exception: ',
            exc_info=(exc_type, exc_value, exc_traceback))

    def run(self):
        while True:
            if self.pics_categories:
                module = PicsSendingModule(self)
                self.modules.append(module)
                module.run()

                module = PicsSuggestionModule(self)
                self.modules.append(module)
                module.run()

            self.loop.create_task(self.client.start(self.token))

            try:
                self.loop.run_forever()
            except (SystemExit, KeyboardInterrupt):
                self.stop('Shutting down.')
                break
            else:
                if self.shutdown_allowed:
                    break
                else:
                    self._init()

    def stop(self, msg=None, timeout=None):
        if msg is not None:
            self.logger.info(self._log_prefix + msg)
        self.loop.create_task(self.close(timeout))
        self.loop.run_forever()
        self.loop.close()

    async def close(self, timeout=None):
        for module in self.modules:
            module.stop(timeout)
        close_tasks = [module.close_task for module in self.modules]
        await asyncio.gather(*close_tasks)

        await self.client.close()
        tasks = [t for t in asyncio.all_tasks()
                 if t is not asyncio.current_task()]
        await asyncio.gather(*tasks)
        self.loop.stop()

    def get_module(self, module_type):
        for module in self.modules:
            if isinstance(module, module_type):
                return module
        return None
