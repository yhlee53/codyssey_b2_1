"""공통 유틸리티 함수들을 모아둔 모듈입니다.

날짜/월 파싱, 태그 분리, 통화 형식 지정, 거래 ID 생성 같은 반복적인 처리 로직을
여기서 통일하여 재사용 가능하게 만든다.
"""

from typing import Optional, List
import datetime


def parse_date(s: str) -> Optional[datetime.date]:
    """문자열 날짜를 `YYYY-MM-DD` 형식으로 파싱해 date 객체로 변환한다.

    잘못된 형식이면 None을 반환해 입력 검증에서 쉽게 사용할 수 있다.
    """
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_month(s: str) -> Optional[datetime.date]:
    """문자열 월을 `YYYY-MM` 형식으로 파싱해 날짜 객체로 변환한다.

    월별 요약 기능에서 사용된다.
    """
    try:
        return datetime.datetime.strptime(s, "%Y-%m").date()
    except Exception:
        return None


def parse_tags(s: str) -> List[str]:
    """콤마 구분 문자열을 태그 리스트로 변환한다.

    예: '식대,점심' -> ['식대', '점심']
    """
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]


def format_currency(amount: int) -> str:
    """정수를 통화 표현 문자열로 변환한다.

    예: 15000 -> '15,000원'
    """
    return f"{amount:,}원"


def gen_tx_id(n: int) -> str:
    """거래 번호를 생성한다.

    예: 1 -> 'TX-000001'
    """
    return f"TX-{n:06d}"
