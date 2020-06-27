async def message_restart(message, args_str, bot):
    if message.author.guild_permissions.administrator:
        await bot.close()
