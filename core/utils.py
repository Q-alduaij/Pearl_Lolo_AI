import time
import random
from typing import Callable, TypeVar

T = TypeVar("T")


def retry(
    fn: Callable[[], T],
    attempts: int = 3,
    base_delay: float = 0.4,
    max_delay: float = 2.5,
) -> T:
    last_err = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if i == attempts - 1:
                break
            delay = min(max_delay, base_delay * (2 ** i)) * (1 + random.random() * 0.25)
            time.sleep(delay)
    raise last_err
