from .ping import message_ping
from .qsize import message_qsize
from .shutdown import message_shutdown


async def message_bot_channel(message, client, command_prefix,
                              pics_categories, logger):
    msg = message.content  # type: str
    if len(msg) > 1 and msg[0] == command_prefix:
        command, *args_str = msg[1:].split(maxsplit=1)
        args_str = args_str[0] if args_str else ''

        if command == 'ping':
            await message_ping(message, args_str)
        elif command == 'qsize':
            await message_qsize(message, args_str, pics_categories)
        elif command == 'shutdown':
            await message_shutdown(message, client, logger)
