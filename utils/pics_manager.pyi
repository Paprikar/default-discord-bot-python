from .discord_bot_container import DiscordBotContainer


class PicsManager:

    def __init__(self, category_name: str, container: DiscordBotContainer): ...

    async def run(self): ...
