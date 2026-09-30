from typing import Optional, List
import datetime


def parse_date(s: str) -> Optional[datetime.date]:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_month(s: str) -> Optional[datetime.date]:
    try:
        return datetime.datetime.strptime(s, "%Y-%m").date()
    except Exception:
        return None


def parse_tags(s: str) -> List[str]:
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]


def format_currency(amount: int) -> str:
    return f"{amount:,}원"


def gen_tx_id(n: int) -> str:
    return f"TX-{n:06d}"
