from discord import Message

from bot.bot import DiscordBot


async def restart(message: Message, args_str: str, bot: DiscordBot):
    """The ``restart`` command.

    Executes a full bot restart.

    Supplement the command with an additional argument of integer type
    to specify a timeout for the restart. After the timeout expires,
    the bot will be forcibly restarted. Default timeout value is ``None``,
    at which the bot will be launched only after its full shutdown.

    Examples:
        !restart

        !restart 10

    Note:
        The user typing this command must have administrator rights
        on the corresponding discord server.

    Args:
        message: Message to be used.
        args_str: String of parameters sent with the command.
        bot: Bot's object.

    """
