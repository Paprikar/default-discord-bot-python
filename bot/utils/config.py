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
        msg = 'Parameter `logging_file` is not a string type.'
        logger.critical(msg)
        raise TypeError(msg)
    if not (logging_file is None
            or path.exists(path.dirname(logging_file))):
        msg = ('Parameter `logging_file` points to a file '
               'in a non-existent folder.')
        logger.critical(msg)
        raise ValueError(msg)
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
        msg = ('Parameter `logging_level` can only be one of the '
               'following values: [1, "DEBUG", 2, "INFO", '
               '3, "WARNING", 4, "ERROR", 5, "CRITICAL"].')
        logger.critical(msg)
        raise ValueError(msg)
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
        msg = 'Parameter `command_prefix` is not a string type.'
        logger.critical(msg)
        raise TypeError(msg)
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
        msg = 'Parameter `pics_categories` is not a dict type.'
        logger.critical(msg)
        raise TypeError(msg)
    if pics_categories is not None:
        for category_name in pics_categories:
            _check_category(
                pics_categories[category_name], category_name, logger)

    return token, command_prefix, bot_channel_id, pics_categories


def _check_category(category, category_name, logger):
    if not isinstance(category_name, str):
        msg = (f'Key `pics_categories/{category_name}` is not a string type.')
        logger.critical(msg)
        raise TypeError(msg)
    if not isinstance(category, dict):
        msg = (f'Value of `pics_categories/{category_name}` '
               'is not a dict type.')
        logger.critical(msg)
        raise TypeError(msg)

    modules = set()
    if _check_pics_sending_module(category, category_name, logger):
        modules.add('PicsSendingModule')
    if _check_pics_suggestion_module(category, category_name, logger):
        modules.add('PicsSuggestionModule')

    category['modules'] = modules


def _check_pics_sending_module(category, category_name, logger):
    keys = {'send_directory',
            'send_channel_id',
            'send_time'}
    if category.keys() & keys:
        if not category.keys() >= keys:
            msg = ('For the sending module to work, it is necessary that the '
                   f'value of `pics_categories/{category_name}` must contain '
                   'the following keys: ["send_directory", '
                   '"send_channel_id", "send_time"].')
            logger.critical(msg)
            raise AssertionError(msg)
    else:
        return False
    #  send_directory
    directory = category['send_directory']
    if not isinstance(directory, str):
        msg = (f'Value of `pics_categories/{category_name}/send_directory` '
               'is not a string type.')
        logger.critical(msg)
        raise TypeError(msg)
    if not path.isdir(directory):
        msg = (f'Value of `pics_categories/{category_name}/send_directory` '
               'should point to an existing folder.')
        logger.critical(msg)
        raise ValueError(msg)
    category['send_directory'] = path.normcase(directory)
    #  send_channel_id
    channel_id = category['send_channel_id']
    if not isinstance(channel_id, int):
        msg = (f'Value of `pics_categories/{category_name}/'
               'send_channel_id` is not an integer type.')
        logger.critical(msg)
        raise TypeError(msg)
    #  send_time
    send_time = category['send_time']
    if not isinstance(send_time, list):
        msg = (f'Value of `pics_categories/{category_name}/'
               'send_time` is not a list type.')
        logger.critical(msg)
        raise TypeError(msg)
    #  send_archive_directory
    directory = category.get('send_archive_directory')
    if directory is None:
        category['send_archive_directory'] = None
    else:
        if not isinstance(directory, str):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'send_archive_directory` is not a string type.')
            logger.critical(msg)
            raise TypeError(msg)
        if not path.isdir(directory):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'send_archive_directory` should point '
                   'to an existing folder.')
            logger.critical(msg)
            raise ValueError(msg)
        category['send_archive_directory'] = path.normcase(directory)

    return True


def _check_pics_suggestion_module(category, category_name, logger):
    keys = {'suggestion_directory',
            'suggestion_channel_id',
            'suggestion_positive',
            'suggestion_negative'}
    if category.keys() & keys:
        if not category.keys() >= keys:
            msg = (
                'For the suggestion module to work, it is necessary that the '
                f'value of `pics_categories/{category_name}` must contain '
                'the following keys: ["suggestion_directory", '
                '"suggestion_channel_id", "suggestion_positive", '
                '"suggestion_negative"].')
            logger.critical(msg)
            raise AssertionError(msg)
    else:
        return False
    #  suggestion_directory
    directory = category['suggestion_directory']
    if not isinstance(directory, str):
        msg = (f'Value of `pics_categories/{category_name}/'
               f'suggestion_directory` is not a string type.')
        logger.critical(msg)
        raise TypeError(msg)
    if not path.isdir(directory):
        msg = (f'Value of `pics_categories/{category_name}/'
               'suggestion_directory` should point to an existing folder.')
        logger.critical(msg)
        raise ValueError(msg)
    category['suggestion_directory'] = path.normcase(directory)
    #  suggestion_channel_id
    channel_id = category['suggestion_channel_id']
    if not isinstance(channel_id, int):
        msg = (f'Value of `pics_categories/{category_name}/'
               'suggestion_channel_id` is not an integer type.')
        logger.critical(msg)
        raise TypeError(msg)
    #  suggestion_positive
    _check_emoji(
        category, category_name, 'suggestion_positive', 'U+2705', logger)
    #  suggestion_negative
    _check_emoji(
        category, category_name, 'suggestion_negative', 'U+274E', logger)

    return True


def _check_emoji(category, category_name, key, default, logger):
    emoji = category.get(key)
    if not (emoji is None or isinstance(emoji, str)):
        msg = (f'Value of `pics_categories/{category_name}/{key}` '
               'is not a string type.')
        logger.critical(msg)
        raise TypeError(msg)
    if emoji is not None:
        try:
            emoji = codepoint_to_str(emoji)
        except ValueError:
            msg = (
                f'Value of `pics_categories/{category_name}/{key}` '
                'must point to a Unicode character.')
            logger.critical(msg)
            raise ValueError(msg)
    if not (emoji is None or len(emoji) == 1):
        msg = (
            f'Value of `pics_categories/{category_name}/{key}` '
            'can only be one symbol after conversion to Unicode.')
        logger.critical(msg)
        raise ValueError(msg)
    if emoji is None:
        logger.info(f'Value of `pics_categories/{category_name}/'
                    f'{key}` is set to "{default}" by default.')
        category[key] = codepoint_to_str(default)
    else:
        category[key] = emoji
