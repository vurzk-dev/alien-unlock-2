import time
from flask import Blueprint, request, jsonify

from logging_config import logger
from paths import USERNAME_RE, USERNAME_MIN, USERNAME_MAX
from get_player_info import (
    create_user, load_user, save_user, list_users, delete_user, user_exists,
)
from get_game_config import get_constants, get_links, get_copy_map
from version import version_c, version_n


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
@bp.route('/version', methods=['GET'])
def api_health():
    return jsonify({
        "status":   "ok",
        "version":  version_c,
        "codename": version_n,
    })


@bp.route('/login', methods=['POST'])
def api_login():
    data     = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()

    if not username:
        return jsonify({"status": "error", "message": "username requerido"}), 400
    if len(username) < USERNAME_MIN or len(username) > USERNAME_MAX:
        return jsonify({
            "status": "error",
            "message": f"longitud inválida ({USERNAME_MIN}-{USERNAME_MAX})"
        }), 400
    if not USERNAME_RE.match(username):
        return jsonify({"status": "error", "message": "caracteres inválidos"}), 400

    existing = load_user(username)
    if existing is not None:
        existing['last_login'] = int(time.time())
        save_user(username, existing)
        logger.info("[~>] [CARGANDO] Login de usuario existente: " + username)
        return jsonify({"status": "ok", "user": existing, "created": False})

    created = create_user(username)
    if created is None:
        return jsonify({"status": "error", "message": "no se pudo crear"}), 500

    logger.info("[+] [CREADO] Login de usuario nuevo: " + username)
    return jsonify({"status": "ok", "user": created, "created": True})


@bp.route('/create_user', methods=['POST'])
def api_create_user():
    data     = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()

    if not username:
        return jsonify({"status": "error", "message": "username requerido"}), 400
    if len(username) < USERNAME_MIN or len(username) > USERNAME_MAX:
        return jsonify({
            "status": "error",
            "message": f"longitud inválida ({USERNAME_MIN}-{USERNAME_MAX})"
        }), 400
    if not USERNAME_RE.match(username):
        return jsonify({"status": "error", "message": "caracteres inválidos"}), 400
    if user_exists(username):
        return jsonify({"status": "error", "message": "usuario ya existe"}), 409

    user = create_user(username)
    if user is None:
        return jsonify({"status": "error", "message": "no se pudo crear"}), 500

    logger.info("[+] [CREADO] Usuario vía API: " + username)
    return jsonify({"status": "ok", "user": user})


@bp.route('/user/<username>', methods=['GET'])
def api_get_user(username):
    u = load_user(username)
    if u is None:
        return jsonify({"status": "error", "message": "usuario no encontrado"}), 404
    return jsonify({"status": "ok", "user": u})


@bp.route('/save_user', methods=['POST'])
def api_save_user():
    data     = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    payload  = data.get('data')

    if not username:
        return jsonify({"status": "error", "message": "username requerido"}), 400
    if not user_exists(username):
        return jsonify({"status": "error", "message": "usuario no existe"}), 404
    if not isinstance(payload, dict):
        return jsonify({"status": "error", "message": "data debe ser objeto"}), 400

    if not save_user(username, payload):
        return jsonify({"status": "error", "message": "no se pudo guardar"}), 500

    return jsonify({"status": "ok"})


@bp.route('/touch_user/<username>', methods=['POST'])
def api_touch_user(username):
    u = load_user(username)
    if u is None:
        return jsonify({"status": "error", "message": "usuario no encontrado"}), 404
    u['last_login'] = int(time.time())
    save_user(username, u)
    return jsonify({"status": "ok"})


@bp.route('/list_users', methods=['GET'])
def api_list_users():
    return jsonify({"status": "ok", "users": list_users()})


@bp.route('/delete_user/<username>', methods=['POST', 'DELETE'])
def api_delete_user(username):
    if delete_user(username):
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "usuario no encontrado"}), 404


@bp.route('/config/constants', methods=['GET'])
def api_config_constants():
    return jsonify({"status": "ok", "constants": get_constants()})


@bp.route('/config/links', methods=['GET'])
def api_config_links():
    return jsonify({"status": "ok", "links": get_links()})


@bp.route('/config/copy', methods=['GET'])
def api_config_copy():
    return jsonify({"status": "ok", "copy": get_copy_map()})