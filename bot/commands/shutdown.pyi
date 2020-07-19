from discord import Message

from bot.bot import DiscordBot


async def message_shutdown(message: Message, args_str: str, bot: DiscordBot): ...
