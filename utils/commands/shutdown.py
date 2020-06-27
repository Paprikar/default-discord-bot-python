async def message_shutdown(message, args_str, container):
    if message.author.guild_permissions.administrator:
        container.shutdown_allowed = True
        await container.discord_bot.close()
