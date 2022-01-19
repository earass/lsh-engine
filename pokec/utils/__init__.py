import time
from functools import wraps
import logging
from datetime import timedelta

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=[
        logging.FileHandler("logs.log"),
        logging.StreamHandler()
    ]
)
logging.root.setLevel(logging.INFO)


def time_summary(func):
    @wraps(func)
    def computation(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f'Total time taken by {func.__name__} is {timedelta(seconds=(end_time - start_time))}')
        return result
    return computation
