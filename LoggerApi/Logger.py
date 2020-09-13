import logging
import datetime
import os


class Logger:
    def __init__(self, filename):
        # create logger
        PATH_NAME = os.path.abspath(os.path.join(__file__, "../../")) + \
                    '\\LOGS_{}'.format(datetime.datetime.now().strftime('%d%m%Y'))
        logging.basicConfig(filename=PATH_NAME, level=logging.DEBUG)
        logger = logging.getLogger(filename)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
        self.__logger = logger

    def add(self, mode, message):
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
