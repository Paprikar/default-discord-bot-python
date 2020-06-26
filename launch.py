import logging
import os

from utils import DiscordBot
from utils import init_logger


def run():
    config_path = 'config.json'
    formatter = logging.Formatter(
        '[%(datetime)s][%(threadName)s][%(name)s]'
        '[%(levelname)s]: %(message)s')
    logger = init_logger(__file__, formatter)
    bot = DiscordBot(config_path, logger, formatter)
    bot.run()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()
