import time
import functools
from typing import Callable, Any
from utils.loggers import time_logger

def measure_time(func: Callable) -> Callable:
    """
    A decorator that measures the execution time of a function.
    
    Args:
        func (Callable): The function to be decorated
        
    Returns:
        Callable: The wrapped function that measures execution time
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        time_logger.info(f"Function '{func.__name__}' took {execution_time:.4f} seconds to execute")
        return result
    
    return wrapper 