from .discord_bot import DiscordBot


class PicsManager:
    bot: DiscordBot

    def __init__(self, category_name: str, bot: DiscordBot): ...

    async def run(self): ...
