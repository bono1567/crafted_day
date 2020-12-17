"""Logger API for the project"""
import logging
import datetime
import os


class Logger:
    """Logger API class."""
    def __init__(self, filename, log_name="LOGS"):
        # create logger
        path_name = os.path.abspath(os.path.join(__file__, "../../")) + \
                    "\\{}_{}".format(log_name, datetime.datetime.now().strftime('%d%m%Y'))
        logging.basicConfig(filename=path_name, level=logging.DEBUG)
        logger = logging.getLogger(filename)

        # create console handler and set level to debug
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        console_handler.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(console_handler)
        self.__logger = logger

    def add(self, mode, message):
        """The add logger line function."""
        if mode == 'DEBUG':
            self.__logger.debug(message)
        elif mode == 'INFO':
            self.__logger.info(message)
        elif mode == 'ERROR':
            self.__logger.error(message)
        elif mode == 'WARN':
            self.__logger.warning(message)
        elif mode == 'CRITICAL':
            self.__logger.critical(message)
