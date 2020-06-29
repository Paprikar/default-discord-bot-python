async def message_shutdown(message, args_str, bot):
    if message.author.guild_permissions.administrator:
        bot.shutdown_allowed = True
        bot.shutdown('Shutting down.')
