from datetime import datetime
from functools import partial, partialmethod
import logging
import os
from src.infrastructure import file_utils

notify_level = 25

today = datetime.now().strftime("%Y%m%d%H%M%S")
log_path = os.path.join(file_utils.LOGS_PATH, "log - " + today + ".txt")

def setup_directories():
    file_utils.create_directory(file_utils.RESULTS_PATH, delete_existing=True)
    file_utils.create_directory(file_utils.LOGS_PATH)
    file_utils.create_directory(file_utils.COMMITS_PATH)

def setup_logging():
    logging.NOTIFY = notify_level
    logging.addLevelName(logging.NOTIFY, 'NOTIFY')
    logging.Logger.notify = partialmethod(logging.Logger.log, logging.NOTIFY)
    logging.notify = partial(logging.log, logging.NOTIFY)

    logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M",
                        filename=log_path, filemode="w", level=notify_level)