import os
import logging

from datetime import datetime
from settings.config import Config
from utils.singleton import Singleton

class LogManager(metaclass=Singleton):

    def __init__(self, file_name: (str | None) = None):
        '''
        Creates a new log file with the `file_name`

        Parameters
        ---------------------------------------------------
        `file_name`: name of the log file

        Returns
        ---------------------------------------------------
        None
        '''
        try:
            LOG_FILE_PATH = (Config().get_instance()).get('LOGGER').get('DIRECTORY')
        except (AttributeError, Exception) as e:
            print('logger file path not provided')
            return
        
        file_name = f'{LOG_FILE_PATH}/{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}.log' if file_name is None else f'{LOG_FILE_PATH}/{file_name}.log'

        if os.path.isfile(file_name):
            os.remove(file_name)

        logger = logging.getLogger('docveclogger')
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(filename=file_name)
        file_formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s\t%(module)s\t%(funcName)s\t%(lineno)d')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s | %(message)s | %(module)s | %(funcName)s | %(lineno)d')
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        self.logger = logger

    def get_logger(self) -> logging.Logger:
        '''
        Returns the logger object

        Parameters
        ---------------------------------------------------
        None

        Returns
        ---------------------------------------------------
        Logger Object
        '''
        return self.logger
