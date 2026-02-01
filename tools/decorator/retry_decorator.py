import time
from functools import wraps

from utils.log_util import logger


def simple_retry(max_retries=3, delay=1):
    """
    简单重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟时间（秒）
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"{func.__name__} 执行失败，{delay}秒后进行第 {attempt + 2} 次重试: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} 执行失败，已达最大重试次数 {max_retries}: {e}")
            raise last_exception

        return wrapper

    return decorator

