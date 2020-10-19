from asyncio import AbstractEventLoop
from asyncio import Task
from logging import Formatter
from logging import Logger
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from discord import Client

from .bot_event_handler import DiscordBotEventHandler
from .moduels import Module
from .utils.config import Config


T_Module = TypeVar('T_Module', bound=Module)


class DiscordBot:
    """Discord bot class.

    Attributes:
        config_path: The path to the json configuration file.
        logger: Logger's object.
        formatter: Formatter's object.
        config: Bot's configuration object.
        loop: The event loop used by the bot.
        client: Bot's client object.
        shutdown_allowed: A flag that allows the bot to shut down.
        event_handler: Bot's event handler object.
        modules: Modules used by the bot.

    """

    config_path: str
    logger: Logger
    formatter: Formatter
    config: Config
    loop: AbstractEventLoop
    client: Client

    shutdown_allowed: bool = False
    event_handler: DiscordBotEventHandler
    modules: List[Type[Module]]

    _client_runner_task: Optional[Task]

    def __init__(self, config_path: str, logger: Optional[Logger], formatter: Optional[Formatter]):
        """
        Args:
            config_path: The path to the json configuration file.
            logger: Logger's object. By default creates a ``Logger``
                with the name of the variable ``__file__``.
            formatter: Formatter's object. By default creates a ``Formatter``
                with the following format:
                `"[%(datetime)s][%(threadName)s][%(name)s]: %(message)s"`.

        """

    def run(self):
        """Method for launching the bot.

        The bot is turned off by pressing the interrupt key,
        calling the ``stop`` method or executing the ``close`` coroutine.
        """

    async def _client_runner(self): ...

    def stop(self, msg: Optional[str] = None, timeout: Optional[float] = None):
        """Method for shutting down the bot.

        Args:
            msg: Message for logging.
            timeout: Timeout for shutdown. When the timeout expires,
                the bot will be forcibly shut down.

        """

    async def close(self, timeout: Optional[float] = None):
        """Coroutine for shutting down the bot.

        Args:
            timeout: Timeout for shutdown. When the timeout expires,
                the bot will be forcibly shut down.

        """

    def get_module(self, module_type: Type[T_Module]) -> Optional[T_Module]:
        """Method for getting a module object by its type.

        Args:
            module_type: Type of module you are looking for.

        Returns:
            Module of the corresponding type if found, otherwise ``None``.

        """

    def _init(self): ...

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback): ...
