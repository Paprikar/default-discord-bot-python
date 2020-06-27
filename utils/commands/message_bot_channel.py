from .ping import message_ping
from .qsize import message_qsize
from .restart import message_restart
from .shutdown import message_shutdown


async def message_bot_channel(message, container):
    msg = message.content  # type: str
    if len(msg) > 1 and msg[0] == container.command_prefix:
        command, *args_str = msg[1:].split(maxsplit=1)
        args_str = args_str[0] if args_str else ''

        if command == 'ping':
            await message_ping(message, args_str, container)
        elif command == 'qsize':
            await message_qsize(message, args_str, container)
        elif command == 'restart':
            await message_restart(message, args_str, container)
        elif command == 'shutdown':
            await message_shutdown(message, args_str, container)
