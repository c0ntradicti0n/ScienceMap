from contextlib import contextmanager
import time
import logging
logging.captureWarnings(True)
logging.getLogger().setLevel(logging.INFO)


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print ('[{name}] finished in {ms} ms'.format(name=name, ms = int(elapsedTime * 1000)))