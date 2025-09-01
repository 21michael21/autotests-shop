import time
from contextlib import contextmanager

@contextmanager
def time_tracker():
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        result = round(end - start)
        print(f"Время выполнения: {result} секунд")




with time_tracker():
    # Выполнение кода
    time.sleep(1)
