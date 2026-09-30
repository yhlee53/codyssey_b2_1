from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass
class Transaction:
    id: str
    type: str  # 'income' or 'expense'
    date: str  # YYYY-MM-DD
    amount: int  # positive
    category: str
    memo: Optional[str] = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Budget:
    month: str  # YYYY-MM
    amount: int


@dataclass
class Category:
    name: str
