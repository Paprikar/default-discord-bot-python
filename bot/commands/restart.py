async def restart(message, args_str, bot):
    if message.author.guild_permissions.administrator:
        if args_str:
            try:
                timeout = int(args_str)
            except ValueError:
                return
        else:
            timeout = None

        bot.stop('Restarting.', timeout)
