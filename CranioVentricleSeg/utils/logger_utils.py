"""
This module provides utility functions for setting up and configuring loggers.
Functions:
    get_logger(logger_name: str, logger_folder: str = "./CranioVentricleSeg/") -> logging.Logger
        Creates and returns a logger with specified name and folder for log files.
"""

import os
import logging
import shutil
import random
from datetime import datetime

from utils import common_utils


class CranioLogger:
    def __init__(self, logger_name: str, logger_folder: str = "./CranioVentricleSeg/"):
        self.formatter = logging.Formatter(
            "%(name)s - %(asctime)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger_name = logger_name
        self.logger_folder = logger_folder
        self.logger = self.get_logger()

    def get_logger(self) -> logging.Logger:
        """
        Creates and returns a logger with specified name and folder for log files.
        Returns:
            logging.Logger: Configured logger instance.
        The logger will have two handlers:
            - A console handler with INFO level.
            - A file handler with DEBUG level, storing logs in a file named with the current datetime.
        The log format is: "%(name)s - %(asctime)s - %(levelname)s: %(message)s"
        with date format: "%Y-%m-%d %H:%M:%S".
        """
        # Get the logging folder
        logger_folder = os.path.join(self.logger_folder, "logging")
        common_utils.create_path(logger_folder)

        # Get the logger
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_number = random.randint(100000, 999999)
        logger = logging.getLogger(self.logger_name)

        # Set the handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(
            os.path.join(logger_folder, f"logs_{random_number}_{current_datetime}.txt"),
            mode="a",
        )
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Set the formatter
        console_handler.setFormatter(self.formatter)
        file_handler.setFormatter(self.formatter)

        # Set the log levels
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

        return logger

    def update_logger_folder(self, new_logger_folder: str):
        """
        Updates the folder where log files are stored.
        Parameters:
            logger_folder (str): The new folder path for log files.
        """
        print(new_logger_folder)
        # Get old logger file
        old_logger_file = self.logger.handlers[1].baseFilename

        # Copy logger file to new folder
        self.logger_folder = os.path.join(new_logger_folder, "logging")
        common_utils.create_path(self.logger_folder)
        shutil.copy(old_logger_file, self.logger_folder)

        # Remove old file handler
        self.logger.removeHandler(self.logger.handlers[1])
        os.remove(old_logger_file)

        # Add new file handler
        file_handler = logging.FileHandler(
            os.path.join(self.logger_folder, os.path.basename(old_logger_file)),
            mode="a",
        )
        self.logger.addHandler(file_handler)

        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(logging.DEBUG)
