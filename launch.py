import os
import sys
import time
import json
import asyncio
import logging
from datetime import datetime

import discord


os.chdir(os.path.dirname(os.path.abspath(__file__)))

NoneType = type(None)


class DateTimeFilter(logging.Filter):
    def filter(self, record):
        record.datetime = time.strftime('%Y-%m-%d-%H-%M-%S')
        return True

logger = logging.getLogger('launch.py')
logger.setLevel(logging.INFO)
logger.addFilter(DateTimeFilter())

formatter = logging.Formatter(
        '[%(datetime)s][%(threadName)s][%(name)s][%(levelname)s]: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('launch.log', delay=True)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical('Unhandled exception:',
                    exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception


with open('config.json') as f:
    config = json.load(f)  # type: dict

#  LOGGING_FILE
LOGGING_FILE = config.get('logging_file')
if not (isinstance(LOGGING_FILE, (str, NoneType))):
    logger.warning('Parameter `logging_file` is not a string.')
    LOGGING_FILE = None
if (LOGGING_FILE is not None
    and not os.path.exists(os.path.dirname(LOGGING_FILE))):
    logger.warning('Parameter `logging_file` '
                   'indicates to a file in a non-existent folder.')
    LOGGING_FILE = None
if LOGGING_FILE is None:
    logger.info('Parameter `logging_file` is set to "./launch.log" by default.')
    LOGGING_FILE = 'launch.log'
else:
    LOGGING_FILE = os.path.normcase(LOGGING_FILE)
logger.removeHandler(file_handler)
file_handler = logging.FileHandler(LOGGING_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#  LOGGING_LEVEL
LOGGING_LEVEL = config.get('logging_level')
if LOGGING_LEVEL in (1, 'DEBUG'):
    LOGGING_LEVEL = logging.DEBUG
elif LOGGING_LEVEL in (2, 'INFO'):
    LOGGING_LEVEL = logging.INFO
elif LOGGING_LEVEL in (3, 'WARNING'):
    LOGGING_LEVEL = logging.WARNING
elif LOGGING_LEVEL in (4, 'ERROR'):
    LOGGING_LEVEL = logging.ERROR
elif LOGGING_LEVEL in (5, 'CRITICAL'):
    LOGGING_LEVEL = logging.CRITICAL
elif LOGGING_LEVEL is not None:
    logger.warning('Parameter `logging_level` can only be one of the '
                   'following values:\n[1, "DEBUG", 2, "INFO", 3, '
                   '"WARNING", 4, "ERROR", 5, "CRITICAL"].')
    LOGGING_LEVEL = None
if LOGGING_LEVEL is None:
    logger.info('Parameter `logging_level` is set to "INFO" by default.')
    LOGGING_LEVEL = logging.INFO
logger.setLevel(LOGGING_LEVEL)
#  TOKEN
TOKEN = config.get('token')
if TOKEN is None:
    logger.critical('Parameter `token` is not specified.')
    exit()
if not isinstance(TOKEN, str):
    logger.critical('Parameter `token` is not a string.')
    exit()
#  COMMAND_PREFIX
COMMAND_PREFIX = config.get('command_prefix')
if COMMAND_PREFIX is None:
    logger.info('Parameter `command_prefix` is set to "!" by default.')
if not isinstance(COMMAND_PREFIX, str):
    logger.warning('Parameter `command_prefix` is not a string.')
#  BOT_CHANNEL_ID
BOT_CHANNEL_ID = config.get('bot_channel_id')
if BOT_CHANNEL_ID is None:
    logger.critical('Parameter `bot_channel_id` is not specified.')
    exit()
if not isinstance(BOT_CHANNEL_ID, int):
    logger.critical('Parameter `bot_channel_id` is not an integer.')
    exit()
#  NSFW_CHANNEL_ID
NSFW_CHANNEL_ID = config.get('nsfw_channel_id')
if NSFW_CHANNEL_ID is not None:
    if not isinstance(NSFW_CHANNEL_ID, int):
        logger.warning('Parameter `nsfw_channel_id` is not an integer.')
        NSFW_CHANNEL_ID = None
#  NSFW_PICS_DIR
NSFW_PICS_DIR = config.get('nsfw_pictures_directory')
if not (isinstance(NSFW_PICS_DIR, (str, NoneType))):
    logger.warning('Parameter `nsfw_pictures_directory` is not a string.')
    NSFW_PICS_DIR = None
if NSFW_PICS_DIR is not None and not os.path.exists(NSFW_PICS_DIR):
    logger.warning('Parameter `nsfw_pictures_directory` '
                   'indicates a non-existent folder.')
    NSFW_PICS_DIR = None
if NSFW_PICS_DIR is not None:
    NSFW_PICS_DIR = os.path.normcase(NSFW_PICS_DIR)
#  NSFW_PICS_SEND_TIME
NSFW_PICS_SEND_TIME = config.get('nsfw_pictures_send_time')
if not (isinstance(NSFW_PICS_SEND_TIME, (list, NoneType))):
    logger.warning('Parameter `nsfw_pictures_send_time` is not a list.')
    NSFW_PICS_SEND_TIME = None
NSFW_MSG_IDS_TO_TRACK = {}


client = discord.Client()


@client.event
async def on_ready():
    guilds = client.guilds
    if guilds:
        msg = f'{client.user} is connected to the following servers:'
        for guild in guilds:
            msg += f'\n  {guild.name} (id: {guild.id})'
        logger.info(msg)


@client.event
async def on_message(message: discord.Message):
    await client.wait_until_ready()

    if (message.channel.id == BOT_CHANNEL_ID
        and message.content.lower() == COMMAND_PREFIX + 'ping'):
        await message.channel.send('...pong')

    if (message.channel.id == BOT_CHANNEL_ID
        and message.author.guild_permissions.administrator
        and message.content.lower() == COMMAND_PREFIX + 'shutdown'):
        await client.logout()
        logger.info('Shutdown.')

    if (message.channel.id == BOT_CHANNEL_ID
        and message.content.lower() == COMMAND_PREFIX + 'qsize'):
        qsize = len(get_nsfw_pics_path_list())
        await message.channel.send(f'NSFW pictures queue size: {qsize}')

    #  Messages from bot
    if message.author == client.user:
        await asyncio.sleep(1)

        #  Remove nsfw file
    if message.id in NSFW_MSG_IDS_TO_TRACK:
        path = NSFW_MSG_IDS_TO_TRACK[message.id]
        try:
            os.remove(path)
            del NSFW_MSG_IDS_TO_TRACK[message.id]
        except:
            logger.warning(f'Can not remove "{path}" file from disk.')


async def nsfw_manager():
    await client.wait_until_ready()

    if (NSFW_CHANNEL_ID is None
        or NSFW_PICS_DIR is None
        or NSFW_PICS_SEND_TIME is None): return

    while not client.is_closed():
        permit, send_cooldown, resend_cooldown = send_nsfw_pic_time_check()
        if permit:
            is_sended = await send_nsfw_pic()
            sleep_time = send_cooldown if is_sended else resend_cooldown
        else:
            sleep_time = resend_cooldown
        await asyncio.sleep(sleep_time)


def send_nsfw_pic_time_check():
    #  Returns: permit, send_cooldown, resend_cooldown
    current_time = datetime.strftime(datetime.now(), '%H:%M')
    if current_time in NSFW_PICS_SEND_TIME:
        return True, 60, 1
    else:
        return False, 60, 1


async def send_nsfw_pic():
    channel = client.get_channel(NSFW_CHANNEL_ID)
    pics_path_list = get_nsfw_pics_path_list()

    if not pics_path_list:
        return False

    pic_path = select_pic(pics_path_list)
    with open(pic_path, 'rb') as f:
        message = await channel.send(
            file=discord.File(f, filename=os.path.basename(pic_path)))
    NSFW_MSG_IDS_TO_TRACK[message.id] = pic_path
    return True


def get_nsfw_pics_path_list():
    if not os.path.exists(NSFW_PICS_DIR):
        return list()
    pics_path_list = [
        os.path.join(NSFW_PICS_DIR, path) for path
        in os.listdir(NSFW_PICS_DIR)
        if (os.path.isfile(os.path.join(NSFW_PICS_DIR, path))
            and os.path.splitext(path)[1].lower() in ('.png', '.jpg', '.jpeg'))
    ]
    return pics_path_list


def select_pic(pics):
    #  Sort by file name
    pics = sorted(
        pics,
        key=lambda x: os.path.splitext(os.path.basename(x))[0])
    return pics[0]


client.loop.create_task(nsfw_manager())
client.run(TOKEN)
