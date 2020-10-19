import asyncio
import logging
import sys

import discord

from .bot_event_handler import DiscordBotEventHandler
from .moduels import PicsSendingModule
from .moduels import PicsSuggestionModule
from .utils import Config
from .utils import init_logger


class DiscordBot:

    def __init__(self, config_path, logger=None, formatter=None):
        self._log_prefix = f'{type(self).__name__}: '

        self.config_path = config_path
        self.formatter = (
            logging.Formatter(
                '[%(datetime)s][%(threadName)s][%(name)s]'
                '[%(levelname)s]: %(message)s')
            if formatter is None
            else formatter)
        self.logger = (init_logger(__file__, formatter) if logger is None
                       else logger)

        self._client_runner_task = None

        sys.excepthook = self._handle_unhandled_exception

        self._init()

    def _init(self):
        self.config = Config(self.config_path, self.logger, self.formatter)

        self.loop = asyncio.get_event_loop()
        self.client = discord.Client(loop=self.loop)

        self.shutdown_allowed = False
        self.event_handler = DiscordBotEventHandler(self)
        self.modules = []

        msg = 'Activated modules:\n'
        if self.config.pics_categories:
            msg += '  Pics categories:\n'
            for k in self.config.pics_categories:
                msg += f'    {k}:\n'
                for module in self.config.pics_categories[k]['modules']:
                    msg += f'      {module}\n'
            self.logger.info(self._log_prefix + msg.rstrip())

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, (SystemExit, KeyboardInterrupt)):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error(
            self._log_prefix +
            'Unhandled exception: ',
            exc_info=(exc_type, exc_value, exc_traceback))

    def run(self):
        while True:
            if self.config.pics_categories:
                module = PicsSendingModule(self)
                self.modules.append(module)
                module.run()

                module = PicsSuggestionModule(self)
                self.modules.append(module)
                module.run()

            self._client_runner_task = self.loop.create_task(
                self._client_runner())

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

    async def _client_runner(self):
        try:
            while True:
                try:
                    await self.client.start(self.config.token)
                    break
                except discord.LoginFailure as e:
                    self.logger.critical(
                        self._log_prefix +
                        'Caught an exception of type `discord.LoginFailure` '
                        f'while authorizing the bot\'s client: {e}')
                    self.shutdown_allowed = True
                    self.stop()
                    break
                except Exception as e:
                    timeout = self.config.reconnect_timeout
                    self.logger.error(
                        self._log_prefix +
                        f'Caught an exception of type `{type(e).__name__}` '
                        f'while launching the bot\'s client: {e}')
                    self.logger.info(f'Reconnection after {timeout} seconds.')
                    await self.client.close()
                    self.client = discord.Client(loop=self.loop)
                    self.event_handler = DiscordBotEventHandler(self)
                    await asyncio.sleep(timeout)
        except asyncio.CancelledError:
            pass

    def stop(self, msg=None, timeout=None):
        if msg is not None:
            self.logger.info(self._log_prefix + msg)
        self.loop.create_task(self.close(timeout))

    async def close(self, timeout=None):
        for module in self.modules:
            module.stop(timeout)
        close_tasks = [module.close_task for module in self.modules]
        await asyncio.gather(*close_tasks)

        await self.client.close()
        self._client_runner_task.cancel()

        tasks = [t for t in asyncio.all_tasks()
                 if t is not asyncio.current_task()]
        await asyncio.gather(*tasks)
        self.loop.stop()

    def get_module(self, module_type):
        for module in self.modules:
            if isinstance(module, module_type):
                return module
        return None
