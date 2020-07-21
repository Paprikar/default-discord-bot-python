import datetime
import json
import logging
from os import path


try:
    import psycopg2
except ModuleNotFoundError:
    psycopg2 = None

from .utils import codepoint_to_str


class Config:

    def __init__(self, config_path, logger, formatter):
        self._log_prefix = f'{type(self).__name__}: '
        self._config_path = config_path
        self._logger = logger
        self._formatter = formatter

        self.token = None
        self.command_prefix = None
        self.bot_channel_id = None
        self.db = None
        self.pics_categories = None

        self._parse_config()

    def _parse_config(self):
        logger = self._logger
        if not isinstance(self._config_path, str):
            msg = 'Parameter `config_path` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not path.isfile(self._config_path):
            msg = 'Parameter `config_path` must point to an existing file.'
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)

        with open(self._config_path) as f:
            config = json.load(f)  # type: dict

        #  LOGGING_FILE
        logging_file = config.get('logging_file')
        if not (logging_file is None
                or isinstance(logging_file, str)):
            msg = 'Parameter `logging_file` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not (logging_file is None
                or path.exists(path.dirname(logging_file))):
            msg = ('Parameter `logging_file` points to a file '
                   'in a non-existent folder.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if logging_file is None:
            logger.info(
                self._log_prefix +
                'Parameter `logging_file` is set '
                'to "./launch.py.log" by default.')
            logging_file = 'launch.py.log'
        else:
            logging_file = path.normcase(logging_file)
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                self._logger.removeHandler(handler)
                break
        file_handler = logging.FileHandler(logging_file)
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)

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
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if logging_level is None:
            logger.info(
                self._log_prefix +
                'Parameter `logging_level` is set to "INFO" by default.')
            logging_level = logging.INFO
        logger.setLevel(logging_level)

        #  TOKEN
        token = config.get('token')
        if token is None:
            msg = 'Parameter `token` is not specified.'
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if not isinstance(token, str):
            msg = 'Parameter `token` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        self.token = token

        #  COMMAND_PREFIX
        command_prefix = config.get('command_prefix')
        if not (command_prefix is None
                or isinstance(command_prefix, str)):
            msg = 'Parameter `command_prefix` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if command_prefix is None:
            logger.info(
                self._log_prefix +
                'Parameter `command_prefix` is set to "!" by default.')
            command_prefix = '!'
        self.command_prefix = command_prefix

        #  BOT_CHANNEL_ID
        bot_channel_id = config.get('bot_channel_id')
        if bot_channel_id is None:
            msg = 'Parameter `bot_channel_id` is not specified.'
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if not isinstance(bot_channel_id, int):
            msg = 'Parameter `bot_channel_id` is not an integer type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        self.bot_channel_id = bot_channel_id

        #  DB
        db = config.get('db')
        if db is not None and psycopg2 is None:
            msg = ('For the database to work, '
                   'the module `psycopg2` is required.')
            logger.critical(self._log_prefix + msg)
            raise ModuleNotFoundError(msg)
        if not (db is None or isinstance(db, dict)):
            msg = 'Parameter `db` is not a dict type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if db is not None:
            db = self._check_db(db)
        self.db = db

        #  RECONNECT_TIMEOUT
        reconnect_timeout = config.get('reconnect_timeout')
        if not (reconnect_timeout is None
                or isinstance(reconnect_timeout, (float, int))):
            msg = ('Parameter `reconnect_timeout` '
                   'is not an integer or float type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not (reconnect_timeout is None or reconnect_timeout >= 0):
            msg = 'Parameter `reconnect_timeout` must be non-negative.'
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if reconnect_timeout is None:
            logger.info(
                self._log_prefix +
                'Parameter `reconnect_timeout` is set to "10" by default.')
            reconnect_timeout = 10
        self.reconnect_timeout = reconnect_timeout

        #  PICS_CATEGORIES
        pics_categories = config.get('pics_categories')
        if not (pics_categories is None
                or isinstance(pics_categories, dict)):
            msg = 'Parameter `pics_categories` is not a dict type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if pics_categories is not None:
            for category_name in pics_categories:
                self._check_pics_category(
                    pics_categories[category_name], category_name)
        self.pics_categories = pics_categories

    def _check_db(self, db):
        logger = self._logger
        # dbname
        dbname = db.get('dbname')
        if dbname is None:
            msg = 'Value of `db/dbname` is not specified.'
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if not isinstance(dbname, str):
            msg = 'Value of `db/dbname` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # host
        host = db.get('host')
        if not (host is None or isinstance(host, str)):
            msg = 'Value of `db/host` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # port
        port = db.get('port')
        if not (port is None or isinstance(port, (str, int))):
            msg = 'Value of `db/port` is not a string or integer type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # user
        user = db.get('user')
        if not (user is None or isinstance(user, str)):
            msg = 'Value of `db/user` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # password
        password = db.get('password')
        if not (password is None or isinstance(password, str)):
            msg = 'Value of `db/password` is not a string type.'
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # clearing the extra keys
        db = {k: db[k] for k
              in ('dbname', 'host', 'port', 'user', 'password')}
        # test connection
        try:
            conn = psycopg2.connect(**db)
            conn.close()
        except psycopg2.DatabaseError as e:
            msg = (
                f'Caught an exception of type `psycopg2.{type(e).__name__}` '
                f'during the test connection to the database: {e}')
            logger.critical(self._log_prefix + msg)
            raise psycopg2.DatabaseError(msg)

        return db

    def _check_pics_category(self, category, category_name):
        logger = self._logger
        if not isinstance(category_name, str):
            msg = (f'Key `pics_categories/{category_name}` '
                   f'is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not isinstance(category, dict):
            msg = (f'Value of `pics_categories/{category_name}` '
                   'is not a dict type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)

        modules = set()
        if self._check_pics_sending_module(category, category_name):
            modules.add('PicsSendingModule')
        if self._check_pics_suggestion_module(category, category_name):
            modules.add('PicsSuggestionModule')

        category['modules'] = modules

    def _check_pics_sending_module(self, category, category_name):
        logger = self._logger
        keys = {'send_directory',
                'send_channel_id',
                'send_start',
                'send_end',
                'send_reserve_days'}
        if category.keys() & keys:
            if not category.keys() >= keys:
                msg = ('For the sending module to work, it is necessary '
                       'that the value of `pics_categories/{category_name}` '
                       'must contain the following keys: ["send_directory", '
                       '"send_channel_id", "send_start", '
                       '"send_end", "send_reserve_days"].')
                logger.critical(self._log_prefix + msg)
                raise AssertionError(msg)
        else:
            return False
        #  send_directory
        directory = category['send_directory']
        if not isinstance(directory, str):
            msg = (
                f'Value of `pics_categories/{category_name}/send_directory` '
                'is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not path.isdir(directory):
            msg = (
                f'Value of `pics_categories/{category_name}/send_directory` '
                'should point to an existing folder.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        category['send_directory'] = path.normcase(directory)
        #  send_channel_id
        channel_id = category['send_channel_id']
        if not isinstance(channel_id, int):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'send_channel_id` is not an integer type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        # send_start
        start = category['send_start']
        if not isinstance(start, str):
            msg = (f'Value of `pics_categories/{category_name}/send_start` '
                   'is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        try:
            start = datetime.datetime.strptime(start, '%H:%M').time()
        except ValueError:
            msg = (f'Value of `pics_categories/{category_name}/send_start` '
                   'is invalid.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        category['send_start'] = start
        # send_end
        end = category['send_end']
        if not isinstance(end, str):
            msg = (f'Value of `pics_categories/{category_name}/send_end` '
                   'is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        try:
            end = datetime.datetime.strptime(end, '%H:%M').time()
        except ValueError:
            msg = (f'Value of `pics_categories/{category_name}/send_end` '
                   'is invalid.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        category['send_end'] = end
        # send_reserve_days
        reserve_days = category['send_reserve_days']
        if not isinstance(reserve_days, int):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'send_reserve_days` is not an integer type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if reserve_days < 1:
            msg = (f'Value of `pics_categories/{category_name}/'
                   'send_reserve_days` must be greater than 0.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        #  send_archive_directory
        directory = category.get('send_archive_directory')
        if directory is None:
            category['send_archive_directory'] = None
        else:
            if not isinstance(directory, str):
                msg = (f'Value of `pics_categories/{category_name}/'
                       'send_archive_directory` is not a string type.')
                logger.critical(self._log_prefix + msg)
                raise TypeError(msg)
            if not path.isdir(directory):
                msg = (f'Value of `pics_categories/{category_name}/'
                       'send_archive_directory` should point '
                       'to an existing folder.')
                logger.critical(self._log_prefix + msg)
                raise ValueError(msg)
            category['send_archive_directory'] = path.normcase(directory)

        return True

    def _check_pics_suggestion_module(self, category, category_name):
        logger = self._logger
        keys = {'suggestion_directory',
                'suggestion_channel_id',
                'suggestion_positive',
                'suggestion_negative'}
        if category.keys() & keys:
            if not category.keys() >= keys:
                msg = (
                    'For the suggestion module to work, it is necessary '
                    'that the value of `pics_categories/{category_name}` '
                    'must contain the following keys: '
                    '["suggestion_directory", "suggestion_channel_id", '
                    '"suggestion_positive", "suggestion_negative"].')
                logger.critical(self._log_prefix + msg)
                raise AssertionError(msg)
        else:
            return False
        #  suggestion_directory
        directory = category['suggestion_directory']
        if not isinstance(directory, str):
            msg = (f'Value of `pics_categories/{category_name}/'
                   f'suggestion_directory` is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if not path.isdir(directory):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'suggestion_directory` should point to an existing folder.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        category['suggestion_directory'] = path.normcase(directory)
        #  suggestion_channel_id
        channel_id = category['suggestion_channel_id']
        if not isinstance(channel_id, int):
            msg = (f'Value of `pics_categories/{category_name}/'
                   'suggestion_channel_id` is not an integer type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        #  suggestion_positive
        self._check_emoji(
            category, category_name, 'suggestion_positive', 'U+2705')
        #  suggestion_negative
        self._check_emoji(
            category, category_name, 'suggestion_negative', 'U+274E')

        return True

    def _check_emoji(self, category, category_name, key, default):
        logger = self._logger
        emoji = category.get(key)
        if not (emoji is None or isinstance(emoji, str)):
            msg = (f'Value of `pics_categories/{category_name}/{key}` '
                   'is not a string type.')
            logger.critical(self._log_prefix + msg)
            raise TypeError(msg)
        if emoji is not None:
            try:
                emoji = codepoint_to_str(emoji)
            except ValueError:
                msg = (
                    f'Value of `pics_categories/{category_name}/{key}` '
                    'must point to a Unicode character.')
                logger.critical(self._log_prefix + msg)
                raise ValueError(msg)
        if not (emoji is None or len(emoji) == 1):
            msg = (
                f'Value of `pics_categories/{category_name}/{key}` '
                'can only be one symbol after conversion to Unicode.')
            logger.critical(self._log_prefix + msg)
            raise ValueError(msg)
        if emoji is None:
            logger.info(
                self._log_prefix +
                f'Value of `pics_categories/{category_name}/'
                f'{key}` is set to "{default}" by default.')
            category[key] = codepoint_to_str(default)
        else:
            category[key] = emoji
