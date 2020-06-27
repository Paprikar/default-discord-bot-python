from discord import Message

from ..discord_bot import DiscordBot


async def message_ping(message: Message, args_str: str, bot: DiscordBot): ...
