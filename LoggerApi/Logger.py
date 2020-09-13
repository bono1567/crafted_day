import logging


class Logger:
    def __init__(self, filename):
        # create logger
        logger = logging.getLogger(filename)
        logger.setLevel(logging.DEBUG)

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
