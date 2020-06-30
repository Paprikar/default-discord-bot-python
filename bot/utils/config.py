import json
import logging
from os import path


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
    pics_categories = config.get('pics_categories')  # type: dict
    if not (pics_categories is None
            or isinstance(pics_categories, dict)):
        logger.error(
            'Parameter `pics_categories` is not a dict type.')
        pics_categories = None
    if pics_categories is not None:
        categories_to_remove = []
        for category_name in pics_categories:
            pass_flag = _check_category(
                pics_categories[category_name], category_name, logger)
            if not pass_flag:
                categories_to_remove.append(category_name)
        for category_name in categories_to_remove:
            del pics_categories[category_name]

    return token, command_prefix, bot_channel_id, pics_categories


def _check_category(category, category_name, logger):
    if not isinstance(category_name, str):
        logger.error(f'Key `pics_categories/{category_name}`'
                     'is not a string type.')
        return False
    if not isinstance(category, dict):
        logger.error(f'Value of `pics_categories/{category_name}`'
                     'is not a dict type.')
        return False
    if not category.keys() >= {'send_channel_id', 'suggestion_channel_id',
                               'directory', 'send_time'}:
        logger.error(
            f'Value of `pics_categories/{category_name} must contain '
            'the following keys: ["send_channel_id", "suggestion_channel_id", '
            '"directory", "send_time"].')
        return False
    #  send_channel_id
    channel_id = category['send_channel_id']
    if not isinstance(channel_id, int):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'send_channel_id` is not an integer type.')
        return False
    #  suggestion_channel_id
    channel_id = category['suggestion_channel_id']
    if not isinstance(channel_id, int):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_channel_id` is not an integer type.')
        return False
    #  suggestion_positive
    emoji = category.get('suggestion_positive', None)
    if not (emoji is None or isinstance(emoji, str)):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_positive` is not a string type.')
        emoji = None
    if emoji is not None:
        try:
            emoji = chr(int(emoji.lstrip("U+").zfill(8), 16))
        except ValueError:
            logger.error(
                f'Value of `pics_categories/{category_name}/'
                'suggestion_positive` must point to a Unicode character.')
            emoji = None
    if not (emoji is None or len(emoji) == 1):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_positive` can only be one symbol '
                     'after conversion to Unicode.')
        emoji = None
    if emoji is None:
        logger.info(f'Value of `pics_categories/{category_name}/'
                    'suggestion_positive` is set to " ✅ " by default.')
        category['suggestion_positive'] = '✅'
    else:
        category['suggestion_positive'] = emoji
    #  suggestion_negative
    emoji = category.get('suggestion_negative', None)
    if not (emoji is None or isinstance(emoji, str)):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_negative` is not a string type.')
        emoji = None
    if emoji is not None:
        try:
            emoji = chr(int(emoji.lstrip("U+").zfill(8), 16))
        except ValueError:
            logger.error(
                f'Value of `pics_categories/{category_name}/'
                'suggestion_negative` must point to a Unicode character.')
            emoji = None
    if not (emoji is None or len(emoji) == 1):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'suggestion_negative` can only be one symbol '
                     'after conversion to Unicode.')
        emoji = None
    if emoji is None:
        logger.info(f'Value of `pics_categories/{category_name}/'
                    'suggestion_negative` is set to " ❎ " by default.')
        category['suggestion_negative'] = '❎'
    else:
        category['suggestion_negative'] = emoji
    #  directory
    directory = category['directory']
    if not isinstance(directory, str):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'directory` is not a string type.')
        return False
    if not path.exists(directory):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'directory` should point to an existing folder.')
        return False
    category['directory'] = path.normcase(
        directory)
    #  send_time
    send_time = category['send_time']
    if not isinstance(send_time, list):
        logger.error(f'Value of `pics_categories/{category_name}/'
                     'send_time` is not a list type.')
        return False

    return True
