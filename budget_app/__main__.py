"""`python -m budget_app` 실행 시 호출되는 엔트리 포인트입니다.

`cli.py`의 `main()` 함수를 실행해 사용자가 입력한 명령을 처리합니다.
"""

from .cli import main

if __name__ == "__main__":
    main()
