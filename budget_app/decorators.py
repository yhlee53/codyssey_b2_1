from typing import Callable, Any
import time
import functools
import sys


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SystemExit:
            raise
        except Exception as e:
            print(f"[오류] {e}")
            print("[힌트] 명령어와 입력값을 확인하세요.")
            sys.exit(1)

    return wrapper


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[실행시간] {end-start:.3f}s")
        return result

    return wrapper
