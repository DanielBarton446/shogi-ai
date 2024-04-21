import concurrent.futures
import os
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from typing import Any, Callable, List

from util.common import get_logger

logger = get_logger(__name__)


class MultiProcManager:
    """
    This is a manager for multiprocessing. We should have some checks
    for the number of workers to spawn. This is a simple wrapper around
    the ProcessPoolExecutor.
    """

    def __init__(self, num_workers: int = os.cpu_count() - 2):
        self.num_workers = num_workers

    def spawn_tasks(self, task_lambda: Callable, **kwargs: Any) -> List[Future]:
        futures = []

        with ProcessPoolExecutor(self.num_workers) as executor:
            command: Callable = partial(task_lambda, **kwargs)
            for _ in range(self.num_workers):
                futures.append(executor.submit(command))
        return futures

    # TODO: it would be nice so have List[Any] actually be
    #       of the type: task_lambda return type
    def futures_results(self,
                        futures: List[concurrent.futures.Future],
                        timeout: int) -> List[Any]:
        results = []
        for future in concurrent.futures.as_completed(futures, timeout):
            results.append(future.result())
        return results
