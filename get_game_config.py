import os
import xml.etree.ElementTree as ET

from logging_config import logger
from paths import GAME_XML_DIR, GAME_TEXT_DIR


logger.info("[~>] [CARGANDO] Configuración XML del juego...")

_CACHE = {}


def _load_xml_cached(path):
    if not os.path.exists(path):
        logger.warning("[!] [ADVERTENCIA] XML no encontrado: " + path)
        return None

    mtime  = os.path.getmtime(path)
    cached = _CACHE.get(path)

    if cached and cached['mtime'] == mtime:
        logger.info("[C] [EN CACHÉ] XML reutilizado: " + path)
        return cached['data']

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        logger.error("[X] [ERROR] Parseando XML " + path + ": " + str(e))
        return None

    _CACHE[path] = {'data': root, 'mtime': mtime}
    logger.info("[~>] [CARGANDO] XML leído desde disco: " + path)
    return root


def load_config_xml():
    return _load_xml_cached(os.path.join(GAME_XML_DIR, 'config.xml'))


def get_section(section_name):
    root = load_config_xml()
    if root is None:
        return []
    for section in root.findall('section'):
        if section.get('name') == section_name:
            return [
                {'name': vr.get('name'), 'value': vr.get('value')}
                for vr in section.findall('vr')
            ]
    return []


def get_constants():
    root = load_config_xml()
    if root is None:
        return {}
    result = {}
    for section in root.findall('section'):
        if section.get('name') != 'constants':
            continue
        constants = section.find('constants')
        if constants is None:
            continue
        for entry in constants.findall('entry'):
            for c in entry.findall('const'):
                name = c.get('name')
                if name:
                    result[name] = (c.text or '').strip()
    return result


def load_links_xml():
    return _load_xml_cached(os.path.join(GAME_XML_DIR, 'links.xml'))


def get_links():
    root = load_links_xml()
    if root is None:
        return {}
    return {
        vr.get('name'): {'value': vr.get('value'), 'target': vr.get('target')}
        for vr in root.findall('vr')
    }


def load_copy_xml():
    return _load_xml_cached(os.path.join(GAME_TEXT_DIR, 'copy.xml'))


def get_copy_map():
    root = load_copy_xml()
    if root is None:
        return {}
    return {
        item.get('id'): (item.text or '').strip()
        for item in root.findall('item')
    }


logger.info("[<] [FINALIZADO] Configuración XML cargada.")