from logging import Formatter
from logging import Logger


class DiscordBot:

    def __init__(self, config_apth: str, logger: Logger, formatter: Formatter): ...

    def run(self): ...

    async def close(self): ...
