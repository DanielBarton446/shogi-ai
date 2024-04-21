"""
Common utility functions.
"""

import logging
import os
from datetime import datetime
from logging import getLogger
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the venv logs directory. The log file is named after the
    provided name and the current time.
    """
    logger = getLogger(name)

    venv_dir = os.environ.get("VIRTUAL_ENV")
    if not venv_dir:
        raise ValueError("No virtual environment found.")
    logdir = Path(venv_dir) / "logs"
    if not logdir.exists():
        logdir.mkdir()

    form = "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
    time = datetime.now().strftime("%Y%m%d.%H%M%S")
    logging.basicConfig(
        filename=f"{logdir}/{name}.{time}.log",
        level=logging.INFO,
        format=form,
        datefmt="%H:%M:%S",
    )
    return logger
