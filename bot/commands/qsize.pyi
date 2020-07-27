from discord import Message

from bot.bot import DiscordBot


async def qsize(message: Message, args_str: str, bot: DiscordBot):
    """The ``qsize`` command.

    Sends a message containing the number of images in the queue
    for the corresponding categories.

    List the names of the required categories separated by a space
    to send information about the corresponding categories,
    otherwise send information about all of them.

    Examples:
        !qsize

        !qsize cats dogs

    Args:
        message: Message to be used.
        args_str: String of parameters sent with the command.
        bot: Bot's object.

    """
