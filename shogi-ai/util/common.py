import logging
import os
from datetime import datetime
from logging import getLogger
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    logger = getLogger(name)

    logdir = Path(os.environ.get("VIRTUAL_ENV")) / "logs"
    if not logdir.exists():
        logdir.mkdir()

    form = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
    time = datetime.now().strftime("%Y%m%d.%H%M%S.%f")
    logging.basicConfig(filename=f"{logdir}/{name}.{time}.log",
                        level=logging.INFO, format=form, datefmt='%H:%M:%S')
    return logger
