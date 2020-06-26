async def message_shutdown(message, args_str, container):
    if message.author.guild_permissions.administrator:
        await container.client.logout()
        container.logger.info('Shutdown.')
