import os
import datetime
import logging
from logging.handlers import RotatingFileHandler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR  = os.path.join(BASE_DIR, 'markut-logs')
os.makedirs(LOG_DIR, exist_ok=True)

_session_stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_FILE = os.path.join(LOG_DIR, f'au2_logs_{_session_stamp}.txt')

LOG_FORMAT  = '[%(levelname)s] [%(asctime)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter   = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    LOG_FILE, mode='a', maxBytes=5_000_000, backupCount=3, encoding='utf-8',
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)


def _has_console_handler():
    return any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root_logger.handlers
    )


def _has_session_file_handler():
    for h in root_logger.handlers:
        if isinstance(h, logging.FileHandler):
            if (getattr(h, 'baseFilename', '') or '') == LOG_FILE:
                return True
    return False


if not _has_console_handler():
    root_logger.addHandler(console_handler)

if not _has_session_file_handler():
    root_logger.addHandler(file_handler)

logger = logging.getLogger("server")
logging.getLogger("werkzeug").setLevel(logging.INFO)

logger.info("[+] [CREADO] Registro dual activo: consola + " + LOG_FILE)
logger.info("[i] [AVISO] Rotación automática: 5 MB por archivo, 3 backups.")