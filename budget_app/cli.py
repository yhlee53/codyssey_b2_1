import argparse
from .storage import TransactionRepository, CategoryStore, BudgetStore
from .services import BudgetService
from .decorators import handle_errors
from .utils import parse_date, parse_tags, format_currency
import sys

DATA_DIR = "./data"


@handle_errors
def main():
    parser = argparse.ArgumentParser(prog="budget_app")
    parser.add_argument("--data-dir", default=DATA_DIR)
    sub = parser.add_subparsers(dest="cmd")

    # add
    sub_add = sub.add_parser("add")

    # list
    sub_list = sub.add_parser("list")
    sub_list.add_argument("--limit", type=int, default=10)

    # search
    sub_search = sub.add_parser("search")
    sub_search.add_argument("--from", dest="from_date")
    sub_search.add_argument("--to", dest="to_date")
    sub_search.add_argument("--category")
    sub_search.add_argument("--type")
    sub_search.add_argument("--q")
    sub_search.add_argument("--tag")

    # update
    sub_update = sub.add_parser("update")
    sub_update.add_argument("--id", required=True)
    sub_update.add_argument("--date")
    sub_update.add_argument("--type")
    sub_update.add_argument("--category")
    sub_update.add_argument("--amount", type=int)
    sub_update.add_argument("--memo")
    sub_update.add_argument("--tags")

    # delete
    sub_delete = sub.add_parser("delete")
    sub_delete.add_argument("--id", required=True)

    # category
    sub_cat = sub.add_parser("category")
    cat_sub = sub_cat.add_subparsers(dest="subcmd")
    cat_add = cat_sub.add_parser("add")
    cat_list = cat_sub.add_parser("list")
    cat_remove = cat_sub.add_parser("remove")
    cat_remove.add_argument("--name", required=True)
    cat_remove.add_argument("--replacement")

    # budget
    sub_budget = sub.add_parser("budget")
    bud_sub = sub_budget.add_subparsers(dest="subcmd")
    bud_set = bud_sub.add_parser("set")
    bud_set.add_argument("--month", required=True)
    bud_set.add_argument("--amount", required=True, type=int)

    # summary
    sub_summary = sub.add_parser("summary")
    sub_summary.add_argument("--month", required=True)
    sub_summary.add_argument("--top", type=int, default=3)

    # import/export
    sub_import = sub.add_parser("import")
    sub_import.add_argument("--from", dest="fromfile", required=True)
    sub_export = sub.add_parser("export")
    sub_export.add_argument("--out", required=True)
    sub_export.add_argument("--month")
    sub_export.add_argument("--from", dest="from_date")
    sub_export.add_argument("--to", dest="to_date")

    args = parser.parse_args()
    data_dir = args.data_dir
    tx_path = f"{data_dir}/transactions.jsonl"
    cat_path = f"{data_dir}/categories.jsonl"
    bud_path = f"{data_dir}/budgets.jsonl"

    tx_repo = TransactionRepository(tx_path)
    cat_store = CategoryStore(cat_path)
    bud_store = BudgetStore(bud_path)
    svc = BudgetService(tx_repo, cat_store, bud_store)

    if args.cmd == "add":
        date = input("날짜(YYYY-MM-DD): ").strip()
        if not parse_date(date):
            print("[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).\n[힌트] 예: 2024-01-15")
            sys.exit(1)
        type_ = input("타입(income/expense): ").strip()
        if type_ not in ("income", "expense"):
            print("[오류] 타입은 'income' 또는 'expense'여야 합니다.")
            sys.exit(1)
        while True:
            category = input("카테고리: ").strip()
            if category in cat_store.list():
                break
            print("[오류] 등록되지 않은 카테고리입니다. 등록된 카테고리: ", ",".join(cat_store.list()))
            yn = input("카테고리를 추가하시겠습니까? (y/N): ").strip().lower()
            if yn == "y":
                cat_store.add(category)
                break
        amount_s = input("금액(양수): ").strip()
        try:
            amount = int(amount_s)
            if amount <= 0:
                raise ValueError()
        except Exception:
            print("[오류] 금액은 양의 정수여야 합니다.")
            sys.exit(1)
        memo = input("메모(선택, 엔터로 생략): ").strip()
        tags = parse_tags(input("태그(쉼표로 구분, 엔터로 생략): "))
        tx = svc.add_transaction(type_, date, category, amount, memo, tags)
        print(f"[저장 완료] id={tx.id}")

    elif args.cmd == "list":
        n = 0
        for tx in svc.list_transactions(limit=args.limit):
            print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} | {tx.memo} | {','.join(tx.tags)}")
            n += 1
            if n >= args.limit:
                break

    elif args.cmd == "search":
        for tx in svc.search(from_date=args.from_date, to_date=args.to_date, category=args.category, type_=args.type, q=args.q, tag=args.tag):
            print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} | {tx.memo} | {','.join(tx.tags)}")

    elif args.cmd == "update":
        tags = None
        if args.tags:
            tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        ok = tx_repo.update(args.id, date=args.date, type=args.type, category=args.category, amount=args.amount, memo=args.memo, tags=tags)
        if ok:
            print(f"[수정 완료] id={args.id}")
        else:
            print(f"[오류] ID가 존재하지 않습니다: {args.id}")
            sys.exit(1)

    elif args.cmd == "delete":
        ok = tx_repo.delete(args.id)
        if ok:
            print(f"[삭제 완료] id={args.id}")
        else:
            print(f"[오류] 삭제 실패: {args.id} (존재하지 않는 거래)")
            sys.exit(1)

    elif args.cmd == "category":
        if args.subcmd == "add":
            name = input("카테고리명: ").strip()
            if cat_store.add(name):
                print(f"[저장 완료] category={name}")
            else:
                print("[오류] 추가 실패 (이미 존재하거나 이름이 비어있음)")
                sys.exit(1)
        elif args.subcmd == "list":
            for c in cat_store.list():
                print(f"- {c}")
        elif args.subcmd == "remove":
            ok = cat_store.remove(args.name, tx_repo=tx_repo, replacement=args.replacement)
            if ok:
                print(f"[삭제 완료] category={args.name}")
            else:
                print(f"[오류] 삭제 불가: '{args.name}' 카테고리를 사용하는 거래가 존재합니다.")
                print("[힌트] 해당 카테고리를 삭제하려면 먼저 사용하는 거래의 카테고리를 변경하거나 --replacement로 대체 카테고리를 지정하세요.")
                sys.exit(1)
        else:
            print("[오류] category 서브명령을 지정하세요 (add/list/remove)")
            sys.exit(1)

    elif args.cmd == "budget":
        if args.subcmd == "set":
            bud_store.set(args.month, args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount}원")
        else:
            print("[오류] budget 서브명령을 지정하세요 (set)")
            sys.exit(1)

    elif args.cmd == "summary":
        income, expense, balance, top_cats, budget_amount = svc.summary(args.month, top=args.top)
        if income == 0 and expense == 0 and not top_cats:
            print("데이터 없음")
            sys.exit(0)
        print(f"{args.month} 요약")
        print(f"총 수입: {format_currency(income)}")
        print(f"총 지출: {format_currency(expense)}")
        print(f"잔액: {format_currency(balance)}")
        if budget_amount is not None:
            rate = expense / budget_amount * 100 if budget_amount > 0 else 0
            warn = " (초과)" if expense > budget_amount else ""
            print(f"예산: {format_currency(budget_amount)} (사용률 {rate:.1f}%){warn}")
        print("\n지출 TOP {}".format(args.top))
        for i, (c, s) in enumerate(top_cats, start=1):
            print(f"{i}) {c} {format_currency(s)}")

    elif args.cmd == "export":
        out = args.out
        import csv
        fields = ["date", "type", "category", "amount", "memo", "tags"]
        rows = []
        if args.month:
            ys, ms = args.month.split("-")
            start = f"{ys}-{ms}-01"
            y = int(ys)
            m = int(ms)
            if m == 12:
                end = f"{y+1}-01-01"
            else:
                end = f"{y}-{m+1:02d}-01"
            for tx in tx_repo.stream():
                if start <= tx.date < end:
                    rows.append(tx)
        elif args.from_date or args.to_date:
            for tx in tx_repo.stream():
                if args.from_date and tx.date < args.from_date:
                    continue
                if args.to_date and tx.date > args.to_date:
                    continue
                rows.append(tx)
        else:
            print("[오류] export는 --month 또는 --from/--to 중 하나를 지정해야 합니다.")
            sys.exit(1)
        with open(out, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for tx in rows:
                writer.writerow([tx.date, tx.type, tx.category, tx.amount, tx.memo or "", ",".join(tx.tags)])
        print(f"[완료] {out} ({len(rows)} records)")

    elif args.cmd == "import":
        path = args.fromfile
        import csv
        imported = 0
        skipped = 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get("date", "").strip()
                type_ = row.get("type", "").strip()
                category = row.get("category", "").strip()
                amount_s = row.get("amount", "").strip()
                memo = row.get("memo", "").strip()
                tags = row.get("tags", "").strip()
                if not parse_date(date) or type_ not in ("income", "expense") or not amount_s.isdigit() or category not in cat_store.list():
                    skipped += 1
                    continue
                amount = int(amount_s)
                svc.add_transaction(type_, date, category, amount, memo, parse_tags(tags))
                imported += 1
        print(f"[완료] imported={imported}, skipped={skipped}")

    else:
        parser.print_help()
