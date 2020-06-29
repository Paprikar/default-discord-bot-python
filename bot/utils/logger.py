import logging
import time


class DateTimeFilter(logging.Filter):

    def filter(self, record):
        record.datetime = time.strftime('%Y-%m-%d-%H-%M-%S')
        return True


def init_logger(name, formatter):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addFilter(DateTimeFilter())

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(name + '.log', delay=True)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
