from logging import Logger

from discord import Client


class DiscordBotAttrs:
    client: Client
    logger: Logger
    token: str
    command_prefix: str
    bot_channel_id: int
    pics_categories: dict

    @staticmethod
    def fill_attrs(source, target, names=None):
        if names is None:
            names = (
                'client',
                'logger',
                'token',
                'command_prefix',
                'bot_channel_id',
                'pics_categories',
            )
        for name in names:
            setattr(target, name, getattr(source, name))
