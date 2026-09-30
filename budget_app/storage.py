from __future__ import annotations
from typing import Iterator, Optional, List, Dict
from .models import Transaction, Budget, Category
import json
import os
from .utils import gen_tx_id


class TransactionRepository:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()

    def _read_lines(self) -> Iterator[str]:
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line

    def stream(self) -> Iterator[Transaction]:
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
        return list(self.stream())

    def _next_id(self) -> str:
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
        txs = self.all()
        new = [tx for tx in txs if tx.id != tx_id]
        if len(new) == len(txs):
            return False
        self._rewrite(new)
        return True


class CategoryStore:
    def __init__(self, path: str, default_categories: Optional[List[str]] = None):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()
        self.default = default_categories or ["food", "transport", "rent", "utilities", "entertainment", "salary", "others"]
        self._ensure_init()

    def _ensure_init(self):
        cats = self.list()
        if not cats:
            for c in self.default:
                self.add(c)

    def _read(self) -> List[Category]:
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
        return [c.name for c in self._read()]

    def add(self, name: str) -> bool:
        name = name.strip()
        if not name:
            return False
        if name in self.list():
            return False
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")
        return True

    def remove(self, name: str, tx_repo: Optional[TransactionRepository] = None, replacement: Optional[str] = None) -> bool:
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
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()

    def _read(self) -> List[Budget]:
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
        for b in self._read():
            if b.month == month:
                return b
        return None
