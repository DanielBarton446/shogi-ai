"""
This module is a simple wrapper around the ProcessPoolExecutor
to spawn tasks and get the results from the tasks.

Example usage:
```
from util.multiproc import MultiProcManager
import random

manager = MultiProcManager(num_workers=4)
futures = manager.spawn_tasks(task_lambda=lambda: x, random.randint(1, 10))
results = manager.futures_results(futures, timeout=5)
print(results)
```
"""

import concurrent.futures
import multiprocessing
import os
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from typing import Any, Callable, List

logger = multiprocessing.get_logger()


class MultiProcManager:
    """
    This is a manager for multiprocessing. We should have some checks
    for the number of workers to spawn. This is a simple wrapper around
    the ProcessPoolExecutor.
    """

    def __init__(self, num_workers: int = os.cpu_count() - 2):  # type: ignore
        self.num_workers = num_workers

    def spawn_tasks(self, task_lambda: Callable, **kwargs: Any) -> List[Future]:
        """
        Generate a list of futures from the task_lambda function to be
        created on num_workers processes.
        """
        futures = []

        with ProcessPoolExecutor(self.num_workers) as executor:
            command: Callable = partial(task_lambda, **kwargs)
            for _ in range(self.num_workers):
                futures.append(executor.submit(command))
        return futures

    # It would be nice so have List[Any] actually be
    # of the type: task_lambda return type
    def futures_results(
        self, futures: List[concurrent.futures.Future], timeout: int
    ) -> List[Any]:
        """
        Fetch the results from the futures. This will block until all
        futures are completed or the timeout is reached.
        """
        results = []
        for future in concurrent.futures.as_completed(futures, timeout):
            results.append(future.result())
        return results
