from .ping import message_ping
from .qsize import message_qsize
from .restart import message_restart
from .shutdown import message_shutdown


async def message_bot_channel(message, bot):
    msg = message.content  # type: str
    if (msg.startswith(bot.config.command_prefix) and
        len(msg) > len(bot.config.command_prefix)):
        data = msg[len(bot.config.command_prefix):]
        command, *args_str = data.split(maxsplit=1)
        args_str = args_str[0] if args_str else ''

        if command == 'ping':
            await message_ping(message, args_str, bot)
        elif command == 'qsize':
            await message_qsize(message, args_str, bot)
        elif command == 'restart':
            await message_restart(message, args_str, bot)
        elif command == 'shutdown':
            await message_shutdown(message, args_str, bot)
