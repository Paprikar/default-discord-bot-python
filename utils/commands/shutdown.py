async def message_shutdown(message, client, logger):
    if message.author.guild_permissions.administrator:
        await client.logout()
        logger.info('Shutdown.')
