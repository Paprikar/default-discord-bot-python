async def message_ping(message, args_str, bot):
    if args_str:
        #  TODO Ping a user
        pass
    else:
        await message.channel.send('...pong')
