import json
import logging
from os import path

from .utils import codepoint_to_str


def parse_config(config_path, logger, formatter):
    if not isinstance(config_path, str):
        msg = 'Parameter `config_path` is not a string type.'
        logger.critical(msg)
        raise TypeError(msg)
    if not path.isfile(config_path):
        msg = 'Parameter `config_path` must point to an existing file.'
        logger.critical(msg)
        raise ValueError(msg)

    with open(config_path) as f:
        config = json.load(f)  # type: dict

    #  LOGGING_FILE
    logging_file = config.get('logging_file')
    if not (logging_file is None
            or isinstance(logging_file, str)):
        logger.error('Parameter `logging_file` is not a string type.')
        logging_file = None
    if not (logging_file is None
            or path.exists(path.dirname(logging_file))):
        logger.error('Parameter `logging_file` points to a file '
                     'in a non-existent folder.')
        logging_file = None
    if logging_file is None:
        logger.info('Parameter `logging_file` is set '
                    'to "./launch.py.log" by default.')
        logging_file = 'launch.py.log'
    else:
        logging_file = path.normcase(logging_file)
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            break
    file_handler = logging.FileHandler(logging_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
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
        logger.error(
            'Parameter `logging_level` can only be one of the '
            'following values: [1, "DEBUG", 2, "INFO", '
            '3, "WARNING", 4, "ERROR", 5, "CRITICAL"].')
        logging_level = None
    if logging_level is None:
        logger.info(
            'Parameter `logging_level` is set to "INFO" by default.')
        logging_level = logging.INFO
    logger.setLevel(logging_level)
    #  TOKEN
    token = config.get('token')
    if token is None:
        msg = 'Parameter `token` is not specified.'
        logger.critical(msg)
        raise ValueError(msg)
    if not isinstance(token, str):
        msg = 'Parameter `token` is not a string type.'
        logger.critical(msg)
        raise TypeError(msg)
    #  COMMAND_PREFIX
    command_prefix = config.get('command_prefix')
    if not (command_prefix is None
            or isinstance(command_prefix, str)):
        logger.error(
            'Parameter `command_prefix` is not a string type.')
        command_prefix = None
    if not (command_prefix is None
            or len(command_prefix) == 1):
        logger.error(
            'Parameter `command_prefix` can only be one symbol.')
        command_prefix = None
    if command_prefix is None:
        logger.info(
            'Parameter `command_prefix` is set to "!" by default.')
        command_prefix = '!'
    #  BOT_CHANNEL_ID
    bot_channel_id = config.get('bot_channel_id')
    if bot_channel_id is None:
        msg = 'Parameter `bot_channel_id` is not specified.'
        logger.critical(msg)
        raise ValueError(msg)
    if not isinstance(bot_channel_id, int):
        msg = 'Parameter `bot_channel_id` is not an integer type.'
        logger.critical(msg)
        raise TypeError(msg)
    #  PICS_CATEGORIES
    pics_categories = config.get('pics_categories')
    if not (pics_categories is None
            or isinstance(pics_categories, dict)):
        logger.error(
            'Parameter `pics_categories` is not a dict type.')
        pics_categories = None
    if pics_categories is not None:
        for category_name in pics_categories:
            modules = _check_category(
                pics_categories[category_name], category_name, logger)
            pics_categories[category_name]['modules'] = modules

    return token, command_prefix, bot_channel_id, pics_categories


def _check_category(category, category_name, logger):
    modules = {'PicsSendingModule',
               'PicsSuggestionModule'}

    if not isinstance(category_name, str):
        logger.error(f'Key `pics_categories/{category_name}` '
                     'is not a string type.')
        return set()
    if not isinstance(category, dict):
        logger.error(f'Value of `pics_categories/{category_name}` '
                     'is not a dict type.')
        return set()
    #  directory
    directory = category['directory']
    msg = (
        'For the sending and suggestion modules to work, it is necessary '
        f'that the value of `pics_categories/{category_name}` must contain '
        'the "directory" key.')
    if not isinstance(directory, str):
        logger.error(
            f'Value of `pics_categories/{category_name}/directory` '
            f'is not a string type. {msg}')
        modules.remove('PicsSendingModule')
        modules.remove('PicsSuggestionModule')
    elif not path.isdir(directory):
        logger.error(
            f'Value of `pics_categories/{category_name}/directory` '
            f'should point to an existing folder. {msg}')
        modules.remove('PicsSendingModule')
        modules.remove('PicsSuggestionModule')
    else:
        category['directory'] = path.normcase(directory)

    if ('PicsSendingModule' in modules and
            not _check_pics_sending_module(category, category_name, logger)):
        modules.remove('PicsSendingModule')

    if ('PicsSuggestionModule' in modules and
            not _check_pics_suggestion_module(category, category_name, logger)):
        modules.remove('PicsSuggestionModule')

    return modules


def _check_pics_sending_module(category, category_name, logger):
    keys = {'send_channel_id',
            'send_time'}
    if (category.keys() & keys and not category.keys() >= keys):
        logger.error(
            'For the sending module to work, it is necessary that the '
            f'value of `pics_categories/{category_name}` must contain '
            'the following keys: ["directory", "send_channel_id", '
            '"send_time"].')
        return False
    #  send_channel_id
    channel_id = category['send_channel_id']
    if not isinstance(channel_id, int):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'send_channel_id` is not an integer type.')
        return False
    #  send_time
    send_time = category['send_time']
    if not isinstance(send_time, list):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'send_time` is not a list type.')
        return False

    return True


def _check_pics_suggestion_module(category, category_name, logger):
    keys = {'suggestion_channel_id',
            'suggestion_positive',
            'suggestion_negative'}
    if (category.keys() & keys and not category.keys() >= keys):
        logger.error(
            'For the suggestion module to work, it is necessary that the '
            f'value of `pics_categories/{category_name}` must contain '
            'the following keys: ["directory", "suggestion_channel_id", '
            '"suggestion_positive", "suggestion_negative"].')
        return False
    #  suggestion_channel_id
    channel_id = category['suggestion_channel_id']
    if not isinstance(channel_id, int):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_channel_id` is not an integer type.')
        return False
    #  suggestion_positive
    _check_emoji(category, category_name, 'suggestion_positive', 'U+2705', logger)
    #  suggestion_negative
    _check_emoji(category, category_name, 'suggestion_negative', 'U+274E', logger)

    return True


def _check_emoji(category, category_name, key, default, logger):
    emoji = category.get(key)
    if not (emoji is None or isinstance(emoji, str)):
        logger.error(f'Value of `pics_categories/{category_name}/{key}` '
                     'is not a string type.')
        emoji = None
    if emoji is not None:
        try:
            emoji = codepoint_to_str(emoji)
        except ValueError:
            logger.error(
                f'Value of `pics_categories/{category_name}/{key}` '
                'must point to a Unicode character.')
            emoji = None
    if not (emoji is None or len(emoji) == 1):
        logger.error(
            f'Value of `pics_categories/{category_name}/{key}` '
            'can only be one symbol after conversion to Unicode.')
        emoji = None
    if emoji is None:
        logger.info(f'Value of `pics_categories/{category_name}/'
                    f'{key}` is set to "{default}" by default.')
        category[key] = codepoint_to_str(default)
    else:
        category[key] = emoji
