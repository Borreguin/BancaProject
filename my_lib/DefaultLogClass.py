import os, sys
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
my_lib_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(my_lib_path)
sys.path.append(project_path)
log_path = os.path.join(project_path, "logs")

ROTATING_FILE_HANDLER = {"filename": "default.log", "maxBytes": 5000000, "backupCount": 5, "mode": "a"}


# Default Class for Logging messages about this API
class LogDefaultConfig():
    """
    Default configuration for the logger file:
    """
    rotating_file_handler = None

    def __init__(self, log_name: str = None):
        if log_name is None:
            log_name = "Default.log"

        self.log_file_name = os.path.join(log_path, log_name)
        self.rotating_file_handler = ROTATING_FILE_HANDLER
        self.rotating_file_handler["filename"] = self.log_file_name
        logger = logging.getLogger(log_name)
        formatter = logging.Formatter('%(levelname)s [%(asctime)s] - %(message)s')
        # creating rotating and stream Handler
        R_handler = RotatingFileHandler(**self.rotating_file_handler)
        R_handler.setFormatter(formatter)
        S_handler = StreamHandler(sys.stdout)
        # adding handlers:
        logger.addHandler(R_handler)
        logger.addHandler(S_handler)

        # setting logger in class
        self.logger = logger

        self.level = "info"
        options = ["error", "warning", "info", "debug", "off"]
        if self.level in options:
            if self.level == "error":
                self.logger.setLevel(logging.ERROR)
            if self.level == "warning":
                self.logger.setLevel(logging.WARNING)
            if self.level == "debug":
                self.logger.setLevel(logging.DEBUG)
            if self.level == "info":
                self.logger.setLevel(logging.INFO)
            if self.level == "off":
                self.logger.setLevel(logging.NOTSET)
        else:
            self.logger.setLevel(logging.ERROR)


# Default Class for Logging messages about this API
class DefaultConfig():
    """
    Default configuration for the logger file:
    """
    rotating_file_handler = None

    def __init__(self, log_name: str = None):
        if log_name is None:
            log_name = "Default.log"

        self.log_file_name = os.path.join(log_path, log_name)
        self.rotating_file_handler = ROTATING_FILE_HANDLER
        self.rotating_file_handler["filename"] = self.log_file_name
        logger = logging.getLogger(log_name)
        formatter = logging.Formatter('%(message)s')
        # creating rotating and stream Handler
        R_handler = RotatingFileHandler(**self.rotating_file_handler)
        R_handler.setFormatter(formatter)
        S_handler = StreamHandler(sys.stdout)
        # adding handlers:
        logger.addHandler(R_handler)
        logger.addHandler(S_handler)

        # setting logger in class
        self.logger = logger

        self.level = "info"
        options = ["error", "warning", "info", "debug", "off"]
        if self.level in options:
            if self.level == "error":
                self.logger.setLevel(logging.ERROR)
            if self.level == "warning":
                self.logger.setLevel(logging.WARNING)
            if self.level == "debug":
                self.logger.setLevel(logging.DEBUG)
            if self.level == "info":
                self.logger.setLevel(logging.INFO)
            if self.level == "off":
                self.logger.setLevel(logging.NOTSET)
        else:
            self.logger.setLevel(logging.ERROR)