import logging

from pathlib import Path

BASE_DIR = Path('src').parent


def init_logger(name, level: str | int = "DEBUG", to_stram: bool = True):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_format = "[%(asctime)s-%(name)s-%(funcName)s-%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    if to_stram:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    path = BASE_DIR / Path("logs")
    if not path.exists():
        path.mkdir()
    logging_path_name = path / f"{name}.log"
    file_handler = logging.FileHandler(logging_path_name, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
