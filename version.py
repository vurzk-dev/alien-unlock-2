import logging
logger = logging.getLogger("version")

version_n = "mark"
version_c = "0.1.0"


def migrate_loaded_save(save: dict) -> bool:
    current_version = save.get("version")

    if current_version != version_c:
        save["version"] = version_c
        logger.info(
            "[~] [ACTUALIZADO] Version de guardado migrada: " +
            str(current_version if current_version is not None else "desconocida") +
            " -> " + str(version_c) + " (" + version_n + ")"
        )
        return True

    logger.info("[O] [EXISTE] Version de guardado ya coincide: " + version_c)
    return False