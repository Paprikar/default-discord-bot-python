from .ping import ping
from .qsize import qsize
from .restart import restart
from .shutdown import shutdown


async def message_bot_channel(message, bot):
    msg = message.content  # type: str
    prefix = bot.config.command_prefix
    if msg.startswith(prefix) and len(msg) > len(prefix):
        data = msg[len(prefix):]
        command, *args_str = data.split(maxsplit=1)
        args_str = args_str[0] if args_str else ''

        if command == 'ping':
            await ping(message)
        elif command == 'qsize':
            await qsize(message, args_str, bot)
        elif command == 'restart':
            await restart(message, args_str, bot)
        elif command == 'shutdown':
            await shutdown(message, args_str, bot)
