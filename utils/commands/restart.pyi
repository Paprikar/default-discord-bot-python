from discord import Message

from ..discord_bot_container import DiscordBotContainer


async def message_restart(message: Message, args_str: str, container: DiscordBotContainer): ...