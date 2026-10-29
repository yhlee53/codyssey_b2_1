"""가계부 비즈니스 로직을 담당하는 서비스 계층입니다.

CLI에서 일어난 사용자 요청을 받아, 거래 생성, 검색, 월별 집계 같은
도메인 규칙을 구현한다.
"""

from typing import List, Optional, Iterator, Tuple
from .models import Transaction
from .storage import TransactionRepository, CategoryStore, BudgetStore
from .utils import parse_date, parse_tags, format_currency
import datetime


class BudgetService:
    """거래/카테고리/예산을 조합해 비즈니스 로직을 수행하는 서비스 클래스.

    저장소 계층에 대한 의존성을 받아, 사용자 기능에 필요한 도메인 로직을
    캡슐화한다.
    """

    def __init__(self, tx_repo: TransactionRepository, cat_store: CategoryStore, budget_store: BudgetStore):
        """서비스가 사용할 데이터 저장소들을 주입받아 초기화한다."""
        self.tx_repo = tx_repo
        self.cat_store = cat_store
        self.budget_store = budget_store

    def add_transaction(self, type_: str, date: str, category: str, amount: int, memo: str, tags: List[str]) -> Transaction:
        """새 거래를 생성해 저장소에 추가하고 생성된 객체를 반환한다.

        Args:
            type_: 거래 유형 (`income` 또는 `expense`)
            date: 거래 일자 (`YYYY-MM-DD`)
            category: 카테고리 이름
            amount: 거래 금액
            memo: 메모
            tags: 태그 목록

        Returns:
            저장된 Transaction 객체
        """
        tx = Transaction(id="", type=type_, date=date, amount=amount, category=category, memo=memo, tags=tags)
        return self.tx_repo.add(tx)

    def list_transactions(self, limit: int = 10) -> Iterator[Transaction]:
        """최신순으로 거래를 순회하는 제너레이터를 반환한다.

        전체 거래 목록을 메모리에 한 번에 적재하지 않고, 저장소의 스트림을 직접 순회한다.
        """
        n = 0
        for tx in self.tx_repo.stream():
            if n >= limit:
                break
            yield tx
            n += 1

    def search(self, from_date: Optional[str] = None, to_date: Optional[str] = None, category: Optional[str] = None, type_: Optional[str] = None, q: Optional[str] = None, tag: Optional[str] = None) -> Iterator[Transaction]:
        """조건에 맞는 거래를 필터링해 반환하는 검색 제너레이터.

        전체 데이터 로드 없이 저장소의 stream()을 순회하면서 조건에 맞는 거래만 yield한다.
        """
        def match(tx: Transaction) -> bool:
            """단일 거래가 검색 조건에 맞는지 확인한다."""
            if from_date:
                if tx.date < from_date:
                    return False
            if to_date:
                if tx.date > to_date:
                    return False
            if category and tx.category != category:
                return False
            if type_ and tx.type != type_:
                return False
            if q and q.lower() not in (tx.memo or "").lower():
                return False
            if tag:
                if tag not in tx.tags:
                    return False
            return True

        for tx in self.tx_repo.stream():
            if match(tx):
                yield tx

    def summary(self, month: str, top: int = 3) -> Tuple[int, int, int, List[Tuple[str,int]] , Optional[int]]:
        """지정된 월의 시계열 요약 정보를 계산한다.

        총 수입, 총 지출, 잔액, 상위 카테고리 지출 금액, 월 예산을 함께 반환한다.
        """
        # returns total_income, total_expense, balance, top_categories, budget_amount
        ys, ms = month.split("-")
        start = f"{ys}-{ms}-01"
        # naive month end
        y = int(ys)
        m = int(ms)
        if m == 12:
            end = f"{y+1}-01-01"
        else:
            end = f"{y}-{m+1:02d}-01"
        income = 0
        expense = 0
        cat_sums = {}
        for tx in self.tx_repo.stream():
            if not (start <= tx.date < end):
                continue
            if tx.type == "income":
                income += tx.amount
            else:
                expense += tx.amount
                cat_sums[tx.category] = cat_sums.get(tx.category, 0) + tx.amount
        balance = income - expense
        top_cats = sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)[:top]
        budget = self.budget_store.get(month)
        budget_amount = budget.amount if budget else None
        return income, expense, balance, top_cats, budget_amount
