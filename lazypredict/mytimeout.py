import multiprocessing
from queue import Empty
import time


class TimeoutException(Exception):
    pass


def timeout(seconds):
    """
    Run the function in a separate process and enforce a timeout.
    If it exceeds 'seconds' seconds, raise a TimeoutException.
    """

    def outer(func):
        def inner(*args, **kwargs):
            result_queue = multiprocessing.Queue()

            def target():
                """Run the function and store the result."""
                try:
                    result_queue.put(func(*args, **kwargs))
                except Exception as e:
                    result_queue.put(e)

            process = multiprocessing.Process(target=target)
            start_time = time.time()
            process.start()

            log_counter = 1
            while (time.time() - start_time) < seconds:
                try:
                    result = result_queue.get_nowait()
                except Empty:
                    result = None
                if result is not None:
                    break
                time.sleep(1)
                if (
                    time.time() - start_time
                ) >= 60 * 5 * log_counter:  # log every 5 mins
                    print(f"{time.ctime(time.time())} Watchdog still running...")
                    log_counter += 1
            else:
                print(f"{time.ctime(time.time())} Time is up!")
                result = None

            process.terminate()
            if result is None:
                raise TimeoutError(
                    f"{func.__name__} took longer than {seconds//60} minutes {seconds%60} seconds to complete."
                )
            if isinstance(result, Exception):
                raise result
            return result

        return inner

    return outer
