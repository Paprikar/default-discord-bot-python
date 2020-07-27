from discord import Message

from bot.bot import DiscordBot


async def message_bot_channel(message: Message, bot: DiscordBot):
    """Called when sending the command to the bot.

    Args:
        message: Message to be used.
        bot: Bot's object.

    """
