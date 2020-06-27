async def message_restart(message, args_str, container):
    if message.author.guild_permissions.administrator:
        await container.discord_bot.close()
