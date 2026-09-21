import os
import socket
import threading
import mimetypes

from flask import Flask, request, jsonify, send_from_directory, abort

from logging_config import logger
from paths import (
    WEB_DIR, SAVES_DIR,
    HOST, PORT, POLICY_PORT,
)
from get_player_info import list_users
from version import version_c, version_n

import command


mimetypes.add_type('application/x-shockwave-flash', '.swf')
mimetypes.add_type('application/x-swz',             '.swz')
mimetypes.add_type('video/x-flv',                   '.flv')
mimetypes.add_type('application/xml',               '.xml')
mimetypes.add_type('text/xml',                      '.xml')


app = Flask(__name__)
app.register_blueprint(command.bp)


@app.before_request
def _diag_log_all_requests():
    logger.info(
        "[DIAG] " + request.method + " " + request.path +
        " | Query: " + str(dict(request.args)) +
        " | Remote: " + str(request.remote_addr)
    )


def socket_policy_server(port=POLICY_PORT):
    policy_xml = (
        '<?xml version="1.0"?>'
        '<!DOCTYPE cross-domain-policy SYSTEM '
        '"http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">'
        '<cross-domain-policy>'
            '<site-control permitted-cross-domain-policies="all"/>'
            '<allow-access-from domain="*" to-ports="*" />'
            '<allow-http-request-headers-from domain="*" headers="*" />'
        '</cross-domain-policy>\0'
    ).encode('utf-8')

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', port))
    srv.listen(20)
    logger.info("[>] [INICIADO] Socket policy server escuchando en puerto " + str(port))

    while True:
        conn, _addr = srv.accept()
        try:
            conn.recv(1024)
            conn.sendall(policy_xml)
        except Exception as e:
            logger.error("[X] [ERROR] Fallo en el policy server: " + str(e))
        finally:
            conn.close()


@app.route('/health')
def serve_health_root():
    return jsonify({
        "status":   "ok",
        "version":  version_c,
        "codename": version_n,
    })


@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_from_directory(WEB_DIR, 'index.html')


@app.route('/login.html')
def serve_login():
    return send_from_directory(WEB_DIR, 'login.html')


@app.route('/alien-unlock-2.html')
def serve_game():
    return send_from_directory(WEB_DIR, 'alien-unlock-2.html')


@app.route('/crossdomain.xml')
def serve_crossdomain():
    return (
        '<?xml version="1.0"?>'
        '<!DOCTYPE cross-domain-policy SYSTEM '
        '"http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">'
        '<cross-domain-policy>'
            '<site-control permitted-cross-domain-policies="all"/>'
            '<allow-access-from domain="*" to-ports="*"/>'
        '</cross-domain-policy>',
        200, {'Content-Type': 'application/xml'}
    )


@app.route('/clientaccesspolicy.xml')
def serve_clientaccess():
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<access-policy><cross-domain-access><policy>'
            '<allow-from http-request-headers="*"><domain uri="*"/></allow-from>'
            '<grant-to><resource path="/" include-subpaths="true"/></grant-to>'
        '</policy></cross-domain-access></access-policy>',
        200, {'Content-Type': 'application/xml'}
    )


@app.route('/<path:path>')
def serve_static(path):
    full = os.path.abspath(os.path.join(WEB_DIR, path))
    root = os.path.abspath(WEB_DIR)
    if not full.startswith(root):
        logger.warning("[!] [ADVERTENCIA] Intento de path traversal: " + path)
        abort(403)

    if not os.path.isfile(full):
        logger.warning("[€] [NO ENCONTRADO] " + path)
        abort(404)

    return send_from_directory(os.path.dirname(full), os.path.basename(full))


@app.errorhandler(404)
def _not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"status": "error", "message": "endpoint no encontrado"}), 404
    return ("Not found", 404)


@app.errorhandler(500)
def _server_error(e):
    logger.error("[X] [ERROR] 500 en " + request.path + ": " + str(e))
    return ("Internal server error", 500)


if __name__ == '__main__':
    threading.Thread(target=socket_policy_server, args=(POLICY_PORT,), daemon=True).start()

    logger.info("")
    logger.info("★" * 55)
    logger.info("[>] [INICIADO] ALIEN UNLOCK 2 - SERVIDOR LOCAL")
    logger.info("[i] [AVISO] Web root: " + WEB_DIR)
    logger.info("[i] [AVISO] Saves en: " + SAVES_DIR)
    logger.info("[i] [AVISO] Versión: " + version_c + " (" + version_n + ")")
    logger.info("[i] [AVISO] Abre: http://" + HOST + ":" + str(PORT) + "/")
    logger.info("★" * 55)
    logger.info("")

    app.run(host=HOST, port=PORT, debug=False, threaded=True)