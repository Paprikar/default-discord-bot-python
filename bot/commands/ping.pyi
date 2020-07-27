from discord import Message


async def ping(message: Message):
    """The ``ping`` command.

    Sends the answer "...pong" to the same text channel.
    Used to check if the bot is online.

    Args:
        message: Message to be used.

    """
