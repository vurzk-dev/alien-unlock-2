import os
import json
import time
import shutil

from logging_config import logger
from paths import (
    SAVES_DIR,
    USERNAME_RE, USERNAME_MIN, USERNAME_MAX,
    _active_users, _active_users_lock,
)
from version import migrate_loaded_save


logger.info("[~>] [CARGANDO] Sistema de perfiles y guardado...")


def _user_path(username):
    return os.path.join(SAVES_DIR, f"{username}.json")


def _is_valid_username(username):
    if not username:
        return False
    if not (USERNAME_MIN <= len(username) <= USERNAME_MAX):
        return False
    return bool(USERNAME_RE.match(username))


def _default_save(username):
    now = int(time.time())
    missions = {}
    for i in range(1, 6):
        mid = f"mission{i:02d}"
        missions[mid] = {
            "unlocked":   (i == 1),
            "completed":  False,
            "best_score": 0,
            "best_time":  0,
            "badges":     [],
        }
    return {
        "version":     "0.1.0",
        "username":    username,
        "created_at":  now,
        "last_login":  now,
        "progress": {
            "missions":     missions,
            "total_score":  0,
            "total_badges": 0,
            "code_letters": [],
            "current_mission": None,
        },
    }


def user_exists(username):
    return os.path.exists(_user_path(username))


def create_user(username):
    if not _is_valid_username(username):
        logger.warning("[!] [ADVERTENCIA] Username inválido: " + repr(username))
        return None
    if user_exists(username):
        logger.info("[O] [EXISTE] El usuario ya existe: " + username)
        return None

    os.makedirs(SAVES_DIR, exist_ok=True)
    data = _default_save(username)
    save_user(username, data)
    logger.info("[+] [CREADO] Nuevo perfil inicializado: " + username)
    return data


def load_user(username):
    path = _user_path(username)
    if not os.path.exists(path):
        logger.info("[€] [NO ENCONTRADO] No existe save para: " + username)
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error("[X] [ERROR] No se pudo leer " + path + ": " + str(e))
        return None

    migrate_loaded_save(data)
    logger.info("[~>] [CARGANDO] Perfil cargado: " + username)

    with _active_users_lock:
        _active_users[username] = time.time()

    return data


def save_user(username, state):
    if not _is_valid_username(username):
        logger.error("[X] [ERROR] Intento de guardado con username inválido: " + repr(username))
        return False

    os.makedirs(SAVES_DIR, exist_ok=True)
    path = _user_path(username)
    state['last_login'] = int(time.time())

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("[X] [ERROR] No se pudo escribir " + path + ": " + str(e))
        return False

    with _active_users_lock:
        _active_users[username] = time.time()

    logger.info("[DB] [BASE DE DATOS] Save actualizado: " + username)
    return True


def list_users():
    if not os.path.isdir(SAVES_DIR):
        return []

    result = []
    for name in sorted(os.listdir(SAVES_DIR)):
        if not name.endswith('.json'):
            continue
        path = os.path.join(SAVES_DIR, name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            result.append({
                "username":    d.get('username', name[:-5]),
                "created_at":  d.get('created_at', 0),
                "last_login":  d.get('last_login', 0),
                "modified":    int(os.path.getmtime(path)),
                "total_score": d.get('progress', {}).get('total_score', 0),
            })
        except Exception as e:
            logger.error("[X] [ERROR] Leyendo save " + name + ": " + str(e))

    result.sort(key=lambda x: x['modified'], reverse=True)
    return result


def delete_user(username):
    path = _user_path(username)
    if not os.path.exists(path):
        return False
    try:
        os.remove(path)
        logger.info("[^] [ELIMINADO] Save eliminado: " + username)
        return True
    except Exception as e:
        logger.error("[X] [ERROR] No se pudo eliminar " + path + ": " + str(e))
        return False


def delete_all():
    if os.path.isdir(SAVES_DIR):
        shutil.rmtree(SAVES_DIR)
        os.makedirs(SAVES_DIR, exist_ok=True)
        logger.info("[^] [ELIMINADO] Carpeta saves/ vaciada por completo.")