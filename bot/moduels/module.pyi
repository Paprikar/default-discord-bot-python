from asyncio import Lock
from asyncio import Task
from typing import Optional

from bot.bot import DiscordBot


class Module:
    """Base class for modules.

    Attributes:
         bot: Bot's object.
         to_close: The lock for switching the module to the shutdown mode.
         close_task: The task responsible for shutting down the module.

    """

    bot: DiscordBot
    to_close: Lock
    close_task: Task

    def run(self):
        """Method for launching the module."""

    def stop(self, timeout: Optional[float] = None):
        """Method for shutting down the module.

        Args:
            timeout: Timeout for shutdown. When the timeout expires,
                the module will be forcibly shut down.

        """
