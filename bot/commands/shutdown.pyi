from discord import Message

from bot.bot import DiscordBot


async def shutdown(message: Message, args_str: str, bot: DiscordBot):
    """The ``shutdown`` command.

    Executes a full bot shutdown.

    Supplement the command with an additional argument of integer type
    to specify a timeout for the shutdown. After the timeout expires,
    the bot will be forcibly shutdown. Default timeout value is ``None``,
    at which the bot will wait until it is completely shutdown.

    Examples:
        !shutdown

        !shutdown 10

    Note:
        The user typing this command must have administrator rights
        on the corresponding discord server.

    Args:
        message: Message to be used.
        args_str: String of parameters sent with the command.
        bot: Bot's object.

    """
