"""애플리케이션 데이터 모델을 정의하는 모듈입니다.

거래(Transaction), 예산(Budget), 카테고리(Category) 같은 도메인 객체를 dataclass로
정의하여 파일 저장·서비스 로직에서 공통 구조를 사용하도록 한다.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass
class Transaction:
    """하나의 거래를 표현하는 데이터 클래스.

    거래의 고유 ID, 유형, 일자, 금액, 카테고리, 메모, 태그 정보를 담는다.
    """
    id: str
    type: str  # 'income' or 'expense'
    date: str  # YYYY-MM-DD
    amount: int  # positive
    category: str
    memo: Optional[str] = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Budget:
    """월별 예산 정보를 표현하는 데이터 클래스.

    특정 월에 적용할 예산 금액을 저장한다.
    """
    month: str  # YYYY-MM
    amount: int


@dataclass
class Category:
    """카테고리 이름을 표현하는 단순 데이터 클래스.

    카테고리 목록 파일 저장을 위해 이름만 보관한다.
    """
    name: str
