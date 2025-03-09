# import threading
# import sys


# class TimeoutException(Exception):
#     pass


# def timeout(seconds):
#     """
#     Decorator to run function in a separate thread and enforce a timeout.
#     If the function does not complete in 'seconds' seconds, it raises a TimeoutException.
#     """

#     def outer(func):
#         def inner(*args, **kwargs):
#             result_container = []

#             def target():
#                 """Run the function and store the result."""
#                 try:
#                     result_container.append(func(*args, **kwargs))
#                 except Exception as e:
#                     result_container.append(e)

#             thread = threading.Thread(target=target)
#             thread.start()
#             thread.join(timeout=seconds)  # Wait for function to complete

#             if thread.is_alive():
#                 # If function is still running, stop and raise TimeoutException
#                 print(f"{func.__name__} took too long", file=sys.stderr)
#                 raise TimeoutException(
#                     f"Function {func.__name__} exceeded time limit of {seconds} seconds."
#                 )

#             # Return function result
#             result = result_container[0] if result_container else None
#             if isinstance(result, Exception):
#                 raise result  # Re-raise any exception that occurred inside the function
#             return result

#         return inner

#     return outer


import multiprocessing
from queue import Empty
import time
import sys


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

            while time.time() - start_time < seconds:
                try:
                    result = result_queue.get_nowait()
                except Empty:
                    result = None
                if result is not None:
                    break
                time.sleep(1)
            else:
                result = None

            process.join()
            process.terminate()
            if result is None:
                raise TimeoutError(
                    f"{func.__name__} took longer than {seconds} seconds to complete."
                )
            if isinstance(result, Exception):
                raise result
            return result

        return inner

    return outer
