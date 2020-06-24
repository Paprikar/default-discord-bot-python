import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

import discord


NoneType = type(None)


class DateTimeFilter(logging.Filter):

    def filter(self, record):
        record.datetime = time.strftime('%Y-%m-%d-%H-%M-%S')
        return True


def get_pics_path_list(directory):
    if not os.path.exists(directory):
        return list()
    pics_path_list = [
        os.path.join(directory, path) for path
        in os.listdir(directory)
        if (os.path.isfile(os.path.join(directory, path))
            and (os.path.splitext(path)[1].lower()
                 in ('.png', '.jpg', '.jpeg')))
    ]
    return pics_path_list


class PicsManager():

    def __init__(self, client, category, msg_ids_to_track, logger):
        self.client = client
        self.logger = logger
        self.channel_id = category['channel_id']
        self.pictures_directory = category['pictures_directory']
        self.pictures_send_time = category['pictures_send_time']
        self.msg_ids_to_track = msg_ids_to_track


    async def run(self):
        await self.client.wait_until_ready()

        while not self.client.is_closed():
            (permit,
             send_cooldown,
             resend_cooldown) = self._send_pic_time_check()
            if permit:
                is_sended = await self._send_pic()
                sleep_time = send_cooldown if is_sended else resend_cooldown
            else:
                sleep_time = resend_cooldown
            await asyncio.sleep(sleep_time)


    def _send_pic_time_check(self):
        #  Returns: permit, send_cooldown, resend_cooldown
        current_time = datetime.strftime(datetime.now(), '%H:%M')
        if current_time in self.pictures_send_time:
            return True, 60, 1
        else:
            return False, 60, 1


    async def _send_pic(self):
        channel = self.client.get_channel(self.channel_id)
        pics_path_list = get_pics_path_list(self.pictures_directory)

        if not pics_path_list:
            return False

        pic_path = self._select_pic(pics_path_list)
        pass_flag = False
        try:
            file = discord.File(pic_path, filename=os.path.basename(pic_path))
            await channel.send(file=file)
            pass_flag = True
            file.close()
            try:
                os.remove(pic_path)
            except:
                self.logger.error(
                    f'Can not remove "{pic_path}" file from disk.')
        except Exception as e:
            self.logger.error(
                f'Caught an exception of type `{type(e).__name__}`: {e}')
        return pass_flag


    @staticmethod
    def _select_pic(pics):
        #  Sort by file name
        pics = sorted(
            pics,
            key=lambda x: os.path.splitext(os.path.basename(x))[0])
        return pics[0]


class DiscordBot():

    def __init__(self):
        self.logger = None  # type: logging.Logger
        self.formatter = logging.Formatter(
            '[%(datetime)s][%(threadName)s][%(name)s]'
            '[%(levelname)s]: %(message)s')
        self.client = discord.Client()
        self.token = None  # type: str
        self.command_prefix = None  # type: str
        self.bot_channel_id = None  # type: int
        self.pics_categories = None  # type: dict
        self.msg_ids_to_track = {}

        self.client.event(self.on_ready)
        self.client.event(self.on_message)

        self._init_logger()
        self._parse_config('config.json')


    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.critical('Unhandled exception:',
                             exc_info=(exc_type, exc_value, exc_traceback))


    def _init_logger(self):
        sys.excepthook = self._handle_unhandled_exception

        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.INFO)
        self.logger.addFilter(DateTimeFilter())

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

        file_handler = logging.FileHandler('launch.log', delay=True)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)


    def _check_category(self, category_name):
        categories = self.pics_categories
        if not isinstance(category_name, str):
            self.logger.error(f'Key `pics_categories/{category_name}`'
                              'is not a string type.')
            return False
        if not isinstance(categories[category_name], dict):
            self.logger.error(f'Value of `pics_categories/{category_name}`'
                              'is not a dict type.')
            return False
        if not (categories[category_name].keys()
                >= {'channel_id', 'pictures_directory', 'pictures_send_time'}):
            self.logger.error(
                f'Value of `pics_categories/{category_name} must contain '
                'the following keys:\n'
                '["channel_id", "pictures_directory", "pictures_send_time"].')
            return False
        #  channel_id
        channel_id = categories[category_name]['channel_id']
        if not isinstance(channel_id, int):
            self.logger.error(f'Value of `pics_categories/{category_name}/'
                              'channel_id` is not an integer type.')
            return False
        #  pictures_directory
        pictures_directory = categories[category_name]['pictures_directory']
        if not isinstance(pictures_directory, str):
            self.logger.error(f'Value of `pics_categories/{category_name}/'
                              'pictures_directory` is not a string type.')
            return False
        if not os.path.exists(pictures_directory):
            self.logger.error(f'Value of `pics_categories/{category_name}/'
                              'pictures_directory` indicates '
                              'a non-existent folder.')
            return False
        categories[category_name]['pictures_directory'] = os.path.normcase(
            pictures_directory)
        #  pictures_send_time
        pictures_send_time = categories[category_name]['pictures_send_time']
        if not isinstance(pictures_send_time, list):
            self.logger.error(f'Value of `pics_categories/{category_name}/'
                              'pictures_send_time` is not a list type.')
            return False
        return True


    def _parse_config(self, config_path):
        with open(config_path) as f:
            config = json.load(f)  # type: dict

        #  LOGGING_FILE
        logging_file = config.get('logging_file')
        if not (isinstance(logging_file, (str, NoneType))):
            self.logger.error('Parameter `logging_file` is not a string type.')
            logging_file = None
        if (logging_file is not None
            and not os.path.exists(os.path.dirname(logging_file))):
            self.logger.error('Parameter `logging_file` indicates to a '
                              'file in a non-existent folder.')
            logging_file = None
        if logging_file is None:
            self.logger.info('Parameter `logging_file` is set '
                             'to "./launch.log" by default.')
            logging_file = 'launch.log'
        else:
            logging_file = os.path.normcase(logging_file)
        self.logger.removeHandler(self.logger.handlers[1])
        file_handler = logging.FileHandler(logging_file)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        #  LOGGING_LEVEL
        logging_level = config.get('logging_level')
        if logging_level in (1, 'DEBUG'):
            logging_level = logging.DEBUG
        elif logging_level in (2, 'INFO'):
            logging_level = logging.INFO
        elif logging_level in (3, 'WARNING'):
            logging_level = logging.WARNING
        elif logging_level in (4, 'ERROR'):
            logging_level = logging.ERROR
        elif logging_level in (5, 'CRITICAL'):
            logging_level = logging.CRITICAL
        elif logging_level is not None:
            self.logger.error(
                'Parameter `logging_level` can only be one of the '
                'following values:\n[1, "DEBUG", 2, "INFO", '
                '3, "WARNING", 4, "ERROR", 5, "CRITICAL"].')
            logging_level = None
        if logging_level is None:
            self.logger.info(
                'Parameter `logging_level` is set to "INFO" by default.')
            logging_level = logging.INFO
        self.logger.setLevel(logging_level)
        #  TOKEN
        self.token = config.get('token')
        if self.token is None:
            self.logger.critical('Parameter `token` is not specified.')
            exit()
        if not isinstance(self.token, str):
            self.logger.critical('Parameter `token` is not a string type.')
            exit()
        #  COMMAND_PREFIX
        self.command_prefix = config.get('command_prefix')
        if not isinstance(self.command_prefix, (str, NoneType)):
            self.logger.error(
                'Parameter `command_prefix` is not a string type.')
            self.command_prefix = None
        if len(self.command_prefix) != 1:
            self.logger.error(
                'Parameter `command_prefix` can only be one symbol.')
            self.command_prefix = None
        if self.command_prefix is None:
            self.logger.info(
                'Parameter `command_prefix` is set to "!" by default.')
        #  BOT_CHANNEL_ID
        self.bot_channel_id = config.get('bot_channel_id')
        if self.bot_channel_id is None:
            self.logger.critical(
                'Parameter `bot_channel_id` is not specified.')
            exit()
        if not isinstance(self.bot_channel_id, int):
            self.logger.critical(
                'Parameter `bot_channel_id` is not an integer type.')
            exit()
        #  PICS_CATEGORIES
        self.pics_categories = config.get('pics_categories')  # type: dict
        if not isinstance(self.pics_categories, (dict, NoneType)):
            self.logger.error(
                'Parameter `pics_categories` is not a dict type.')
            self.pics_categories = None
        if self.pics_categories is not None:
            categories_to_remove = []
            for category_name in self.pics_categories:
                pass_flag = self._check_category(category_name)
                if not pass_flag:
                    categories_to_remove.append(category_name)
            for category_name in categories_to_remove:
                del self.pics_categories[category_name]


    async def on_ready(self):
        guilds = self.client.guilds
        if guilds:
            msg = f'{self.client.user} is connected to the following servers:'
            for guild in guilds:
                msg += f'\n  {guild.name} (id: {guild.id})'
            self.logger.info(msg)


    async def on_message(self, message: discord.Message):
        await self.client.wait_until_ready()

        if message.channel.id == self.bot_channel_id:
            await self._on_message_bot_channel(message)


    async def _on_message_bot_channel(self, message):
        msg = message.content  # type: str
        if len(msg) > 1 and msg[0] == self.command_prefix:
            command, *args = msg[1:].split(maxsplit=1)
            args = args[0] if args else None
            if command == 'ping':
                await self._message_ping(message, args)
            elif command == 'shutdown':
                await self._message_shutdown(message)
            elif command == 'qsize':
                await self._message_qsize(message, args)


    async def _message_ping(self, message, args):
        if args:
            #  TODO Ping a user
            pass
        else:
            await message.channel.send('...pong')


    async def _message_shutdown(self, message):
        if message.author.guild_permissions.administrator:
            await self.client.logout()
            self.logger.info('Shutdown.')


    async def _message_qsize(self, message, args):
        category_names = set()
        if 'all' in args:
            category_names.update(self.pics_categories.keys())
        else:
            for category_name in args:
                if category_name in self.pics_categories:
                    category_names.add(category_name)
        if not category_names:
            return
        category_names = sorted(category_names)
        desc = ''
        embed = discord.Embed()
        for category_name in category_names:
            path = self.pics_categories[category_name]['pictures_directory']
            qsize = len(get_pics_path_list(path))
            desc += f'Queue size for `{category_name}` pictures: {qsize}\n'
        embed.description = desc.rstrip()
        await message.channel.send(embed=embed)


    def run(self):
        if self.pics_categories:
            for category in self.pics_categories.values():
                manager = PicsManager(
                    self.client, category, self.msg_ids_to_track, self.logger)
                self.client.loop.create_task(manager.run())

        self.client.run(self.token)


def run():
    bot = DiscordBot()
    bot.run()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()
