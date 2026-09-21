import os
import re
import sys
import threading

from logging_config import logger


def _get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_DIR  = _get_exe_dir()

WEB_DIR         = os.path.join(BASE_DIR, 'web')
TEMPLATES_DIR   = WEB_DIR
GAME_XML_DIR    = os.path.join(WEB_DIR, 'xml')
GAME_TEXT_DIR   = os.path.join(WEB_DIR, 'text')
GAME_CSS_DIR    = os.path.join(WEB_DIR, 'css')
GAME_JS_DIR     = os.path.join(WEB_DIR, 'js')
GAME_ASSETS_DIR = os.path.join(WEB_DIR, 'assets')
GAME_FILES_DIR  = os.path.join(WEB_DIR, 'files')
GAME_IMG_DIR    = os.path.join(WEB_DIR, 'img')

SAVES_DIR = os.path.join(BASE_DIR, 'saves')
os.makedirs(SAVES_DIR, exist_ok=True)

USERNAME_MIN = 3
USERNAME_MAX = 16
USERNAME_RE  = re.compile(r'^[A-Za-z0-9_\-]+$')

HOST        = '127.0.0.1'
PORT        = 8000
POLICY_PORT = 5840

_active_users      = {}
_active_users_lock = threading.Lock()

AUTOSAVE_INTERVAL      = 5
AUTOSAVE_ACTIVE_WINDOW = 30