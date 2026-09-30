from typing import List, Optional, Iterator, Tuple
from .models import Transaction
from .storage import TransactionRepository, CategoryStore, BudgetStore
from .utils import parse_date, parse_tags, format_currency
import datetime


class BudgetService:
    def __init__(self, tx_repo: TransactionRepository, cat_store: CategoryStore, budget_store: BudgetStore):
        self.tx_repo = tx_repo
        self.cat_store = cat_store
        self.budget_store = budget_store

    def add_transaction(self, type_: str, date: str, category: str, amount: int, memo: str, tags: List[str]) -> Transaction:
        tx = Transaction(id="", type=type_, date=date, amount=amount, category=category, memo=memo, tags=tags)
        return self.tx_repo.add(tx)

    def list_transactions(self, limit: int = 10) -> Iterator[Transaction]:
        # latest first
        for tx in reversed(self.tx_repo.all()):
            yield tx

    def search(self, from_date: Optional[str] = None, to_date: Optional[str] = None, category: Optional[str] = None, type_: Optional[str] = None, q: Optional[str] = None, tag: Optional[str] = None) -> Iterator[Transaction]:
        def match(tx: Transaction) -> bool:
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

        for tx in reversed(self.tx_repo.all()):
            if match(tx):
                yield tx

    def summary(self, month: str, top: int = 3) -> Tuple[int, int, int, List[Tuple[str,int]] , Optional[int]]:
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
