"""공통 CLI 데코레이터를 정의하는 모듈입니다.

이 모듈은 예외 처리와 실행 시간 로깅을 표준화해서, 각 기능 함수가
중복된 에러 처리 코드를 직접 작성하지 않도록 돕습니다.
"""

from typing import Callable, Any
import time
import functools
import sys


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """함수 실행 중 발생한 예외를 사용자 친화적인 메시지로 변환한다.

    `SystemExit`은 그대로 전달하고, 그 외 예외는 콘솔에 `[오류]` 메시지와 힌트 텍스트를
    출력한 뒤 프로세스 종료 코드를 1로 설정한다.
    """
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
    """함수의 실행 시간을 측정해 로그로 출력하는 데코레이터.

    기능의 성능을 추적할 때 사용하며, 특히 파일 I/O나 검색 로직이 많은 상황에서
    병목 지점을 찾는 데 도움이 된다.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[실행시간] {end-start:.3f}s")
        return result

    return wrapper
