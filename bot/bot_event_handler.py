import inspect

from .commands import message_bot_channel
from .moduels import PicsSuggestionModule


class DiscordBotEventHandler:

    def __init__(self, bot):
        self._log_prefix = f'{type(self).__name__}: '

        self.bot = bot
        self.isModulesStarted = False

        methods = inspect.getmembers(self, inspect.ismethod)
        events = (method[1] for method in methods
                  if method[0].startswith('on_'))
        for event in events:
            self.update_event(event)

    def update_event(self, event):
        self.bot.client.event(event)

    async def on_connect(self):
        pass

    async def on_disconnect(self):
        pass

    async def on_ready(self):
        guilds = self.bot.client.guilds
        if not guilds:
            return
        msg = (f'{self.bot.client.user} '
               'is connected to the following servers:')
        for guild in guilds:
            msg += f'\n  {guild.name} (id: {guild.id})'
        self.bot.logger.info(self._log_prefix + msg)

        if not self.isModulesStarted:
            self.isModulesStarted = True
            for module in self.bot.modules:
                module.run()

    async def on_shard_ready(self, shard_id):
        pass

    async def on_resumed(self):
        pass

    async def on_error(self, event, *args, **kwargs):
        pass

    async def on_socket_raw_receive(self, msg):
        pass

    async def on_socket_raw_send(self, payload):
        pass

    async def on_typing(self, channel, user, when):
        pass

    async def on_message(self, message):
        if message.channel.id == self.bot.config.bot_channel_id:
            await message_bot_channel(message, self.bot)

    async def on_message_delete(self, message):
        pass

    async def on_bulk_message_delete(self, messages):
        pass

    async def on_raw_message_delete(self, payload):
        pass

    async def on_raw_bulk_message_delete(self, payload):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_raw_message_edit(self, payload):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_raw_reaction_add(self, payload):
        #  PicsSuggestionModule
        module = self.bot.get_module(PicsSuggestionModule)
        await module.reaction_handler(payload)

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_raw_reaction_remove(self, payload):
        pass

    async def on_reaction_clear(self, message, reactions):
        pass

    async def on_raw_reaction_clear(self, payload):
        pass

    async def on_reaction_clear_emoji(self, reaction):
        pass

    async def on_raw_reaction_clear_emoji(self, payload):
        pass

    async def on_private_channel_delete(self, channel):
        pass

    async def on_private_channel_create(self, channel):
        pass

    async def on_private_channel_update(self, before, after):
        pass

    async def on_private_channel_pins_update(self, channel, last_pin):
        pass

    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_channel_create(self, channel):
        pass

    async def on_guild_channel_update(self, before, after):
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    async def on_guild_integrations_update(self, guild):
        pass

    async def on_webhooks_update(self, channel):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, before, after):
        pass

    async def on_user_update(self, before, after):
        pass

    async def on_guild_join(self, guild):
        pass

    async def on_guild_remove(self, guild):
        pass

    async def on_guild_update(self, before, after):
        pass

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass

    async def on_guild_role_update(self, before, after):
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        pass

    async def on_guild_available(self, guild):
        pass

    async def on_guild_unavailable(self, guild):
        pass

    async def on_voice_state_update(self, member, before, after):
        pass

    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass

    async def on_invite_create(self, invite):
        pass

    async def on_invite_delete(self, invite):
        pass

    async def on_group_join(self, channel, user):
        pass

    async def on_group_remove(self, channel, user):
        pass

    async def on_relationship_add(self, relationship):
        pass

    async def on_relationship_remove(self, relationship):
        pass

    async def on_relationship_update(self, before, after):
        pass
