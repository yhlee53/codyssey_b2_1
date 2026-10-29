"""데이터 파일 접근과 영속화 로직을 담당하는 저장소 계층입니다.

거래, 카테고리, 예산 데이터를 각각 JSONL 파일로 관리하며,
파일 쓰기/삭제/업데이트 시 임시 파일을 통해 원자성을 보장한다.
"""

from __future__ import annotations
from typing import Iterator, Optional, List, Dict
from .models import Transaction, Budget, Category
import json
import os
from .utils import gen_tx_id


class TransactionRepository:
    """거래 데이터를 `transactions.jsonl`에 저장하고 관리하는 저장소 클래스.

    파일을 한 줄씩 읽는 제너레이터 기반 인터페이스를 제공해 대용량 데이터도 순회 가능하게 한다.
    """

    def __init__(self, path: str):
        """저장 경로를 받아 디렉터리를 생성하고 파일이 없으면 빈 파일로 초기화한다."""
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()

    def _read_lines(self) -> Iterator[str]:
        """JSONL 파일의 각 줄을 읽어 문자열 iterator로 반환한다."""
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line

    def stream(self) -> Iterator[Transaction]:
        """JSONL 파일을 읽어 Transaction 객체들을 순차적으로 생성해 반환한다."""
        for line in self._read_lines():
            data = json.loads(line)
            tx = Transaction(
                id=data["id"],
                type=data["type"],
                date=data["date"],
                amount=int(data["amount"]),
                category=data["category"],
                memo=data.get("memo", ""),
                tags=data.get("tags", []),
            )
            yield tx

    def all(self) -> List[Transaction]:
        """모든 거래를 리스트로 반환한다.

        전체 데이터를 메모리에 올리므로 작은 규모의 로직에서 간편하게 사용한다.
        """
        return list(self.stream())

    def _next_id(self) -> str:
        """마지막 거래 ID를 기반으로 다음 거래 ID를 생성한다."""
        max_n = 0
        for tx in self.stream():
            try:
                n = int(tx.id.split("-")[1])
                if n > max_n:
                    max_n = n
            except Exception:
                continue
        return gen_tx_id(max_n + 1)

    def add(self, tx: Transaction) -> Transaction:
        """새 거래를 파일에 추가하고, 생성된 ID를 반영해 반환한다."""
        if not tx.id:
            tx.id = self._next_id()
        with open(self.path, "a", encoding="utf-8") as f:
            d = {
                "id": tx.id,
                "type": tx.type,
                "date": tx.date,
                "amount": tx.amount,
                "category": tx.category,
                "memo": tx.memo,
                "tags": tx.tags,
            }
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
        return tx

    def _rewrite(self, txs: List[Transaction]):
        """거래 목록 전체를 임시 파일에 써서 원자적으로 교체한다."""
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for tx in txs:
                d = {
                    "id": tx.id,
                    "type": tx.type,
                    "date": tx.date,
                    "amount": tx.amount,
                    "category": tx.category,
                    "memo": tx.memo,
                    "tags": tx.tags,
                }
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        os.replace(tmp, self.path)

    def update(self, tx_id: str, **fields) -> bool:
        """특정 거래 ID를 찾아 필드를 수정한다.

        변경이 있으면 전체 파일을 다시 작성해 반영한다.
        """
        modified = False
        txs = self.all()
        for tx in txs:
            if tx.id == tx_id:
                for k, v in fields.items():
                    if hasattr(tx, k) and v is not None:
                        setattr(tx, k, v)
                modified = True
                break
        if modified:
            self._rewrite(txs)
        return modified

    def delete(self, tx_id: str) -> bool:
        """지정된 거래 ID를 제거한다.

        삭제 대상이 없으면 False를 반환하고, 있으면 새 파일로 교체한다.
        """
        txs = self.all()
        new = [tx for tx in txs if tx.id != tx_id]
        if len(new) == len(txs):
            return False
        self._rewrite(new)
        return True


class CategoryStore:
    """카테고리 목록을 JSONL로 관리하는 저장소 클래스.

    기본 카테고리를 초기화하고, 추가/삭제/대체 로직을 담당한다.
    """

    def __init__(self, path: str, default_categories: Optional[List[str]] = None):
        """저장 경로와 기본 카테고리 목록을 설정하고 초기 데이터를 준비한다."""
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()
        self.default = default_categories or ["food", "transport", "rent", "utilities", "entertainment", "salary", "others"]
        self._ensure_init()

    def _ensure_init(self):
        """카테고리 파일이 비어 있으면 기본 카테고리를 자동으로 추가한다."""
        cats = self.list()
        if not cats:
            for c in self.default:
                self.add(c)

    def _read(self) -> List[Category]:
        """JSONL 파일에서 Category 객체 목록을 읽어온다."""
        with open(self.path, "r", encoding="utf-8") as f:
            data = f.read().strip().splitlines()
        res = []
        for line in data:
            try:
                obj = json.loads(line)
                res.append(Category(name=obj["name"]))
            except Exception:
                continue
        return res

    def list(self) -> List[str]:
        """카테고리 이름만 리스트로 반환한다."""
        return [c.name for c in self._read()]

    def add(self, name: str) -> bool:
        """새 카테고리를 파일에 추가한다.

        이름이 비어 있거나 이미 존재하면 False를 반환한다.
        """
        name = name.strip()
        if not name:
            return False
        if name in self.list():
            return False
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")
        return True

    def remove(self, name: str, tx_repo: Optional[TransactionRepository] = None, replacement: Optional[str] = None) -> bool:
        """카테고리를 삭제한다.

        해당 카테고리를 사용하는 거래가 있으면 replacement가 제공된 경우만 대체하고,
        그렇지 않으면 삭제를 막는다.
        """
        # if transactions use it, prevent unless replacement provided
        if tx_repo:
            for tx in tx_repo.stream():
                if tx.category == name:
                    if replacement:
                        tx_repo.update(tx.id, category=replacement)
                    else:
                        return False
        cats = [c for c in self._read() if c.name != name]
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for c in cats:
                f.write(json.dumps({"name": c.name}, ensure_ascii=False) + "\n")
        os.replace(tmp, self.path)
        return True


class BudgetStore:
    """월별 예산 정보를 `budgets.jsonl` 파일로 관리하는 저장소 클래스."""

    def __init__(self, path: str):
        """예산 파일 경로를 설정하고, 파일이 없으면 빈 파일로 초기화한다."""
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()

    def _read(self) -> Iterator[Budget]:
        """예산 파일을 읽어 Budget 객체 리스트로 변환한다."""
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    yield Budget(month=obj["month"], amount=int(obj["amount"]))
                except Exception:
                    continue

    def set(self, month: str, amount: int):
        """특정 월의 예산 값을 저장하거나 갱신한다.

        기존 값이 있으면 업데이트하고, 없으면 새로 추가한 뒤 임시 파일로 교체한다.
        """
        # replace existing or append
        budgets = list(self._read())
        updated = False
        for b in budgets:
            if b.month == month:
                b.amount = amount
                updated = True
                break
        if not updated:
            budgets.append(Budget(month=month, amount=amount))
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for b in budgets:
                f.write(json.dumps({"month": b.month, "amount": b.amount}, ensure_ascii=False) + "\n")
        os.replace(tmp, self.path)

    def get(self, month: str) -> Optional[Budget]:
        """지정한 월의 예산 객체를 반환한다. 없으면 None을 반환한다."""
        for b in self._read():
            if b.month == month:
                return b
        return None
