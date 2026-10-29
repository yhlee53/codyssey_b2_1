용돈 기입장 (budget_app)

요구사항에 맞춘 콘솔 기반 가계부 애플리케이션입니다.

실행 환경
- Python 3.10 이상
- 외부 라이브러리 필요 없음(표준 라이브러리만 사용)

설치/실행
- 소스 루트에서 아래처럼 실행합니다:
  python -m budget_app <command> [options]

예: 거래 추가
  python -m budget_app add

기본 데이터 폴더 및 파일
- 기본 데이터 폴더: ./data (--data-dir 옵션으로 변경 가능)
- 저장 파일(영구 저장, JSONL 포맷):
  - ./data/transactions.jsonl
  - ./data/categories.jsonl
  - ./data/budgets.jsonl

CSV import/export 스키마 (UTF-8, 헤더 포함)
- 컬럼: date,type,category,amount,memo,tags
- 예:
  date,type,category,amount,memo,tags
  2024-01-15,expense,food,15000,점심,meal,lunch

주요 명령 및 옵션
- 1. add
  - 대화형으로 거래 추가 (date, type, category, amount, memo, tags)
    python -m budget_app add           
      날짜(YYYY-MM-DD): 2026-10-09
      타입(income/expense): expense
      카테고리:  rent
      금액(양수): 20000
      메모(선택, 엔터로 생략): 모니터
      태그(쉼표로 구분, 엔터로 생략): 모니터, 20inch
      [저장 완료] id=TX-000021

- 2. list --limit N
  - 최신순 거래 출력 (기본 limit=10)
    python -m budget_app list --limit 5                 
      TX-000020 | 2026-10-08 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000019 | 2026-10-07 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000018 | 2026-10-06 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000017 | 2026-10-05 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000016 | 2026-09-05 | expense | food | 10000 | 점심식대 | 식대,점심

- 3. search --from YYYY-MM-DD --to YYYY-MM-DD --category NAME --type income|expense --q KEYWORD --tag TAG
    python -m budget_app search --from 2026-10-01 --to 2026-10-06  
      TX-000018 | 2026-10-06 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000017 | 2026-10-05 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000009 | 2026-10-01 | income | salary | 1000000 | 10월 급여 | 월,급여
    python -m budget_app search --from 2026-10-01 --to 2026-10-06 --category food --type expense --q 점 --tag 식대
      TX-000018 | 2026-10-06 | expense | food | 10000 | 점심식대 | 식대,점심
      TX-000017 | 2026-10-05 | expense | food | 10000 | 점심식대 | 식대,점심

- 4. summary --month YYYY-MM --top N
  - 월별 요약 (총수입/총지출/잔액 + 카테고리별 지출 TOP N), 예산 사용률/초과 표시
    python -m budget_app summary --month 2026-10 --top 5 
      총 수입: 1,000,000원
      총 지출: 60,000원
      잔액: 940,000원
      예산: 50,000원 (사용률 120.0%) (초과)

      지출 TOP 5
      1) food 40,000원
      2) rent 20,000원

- 5. budget set --month YYYY-MM --amount AMOUNT
  - 월 예산 설정
    python -m budget_app budget set --month 2026-03 --amount 55000
      [저장 완료] 2026-03 예산 55000원

- 6. category add | list | remove --name NAME [--replacement NAME]
  - 카테고리 관리 (삭제 시 사용 중이면 replacement로 대체하거나 삭제 차단)
    python -m budget_app category add           
      카테고리명: aaa
      [저장 완료] category=aaa
    python -m budget_app category remove --name aaa
      [삭제 완료] category=aaa
    python -m budget_app category remove --name food
      [오류] 삭제 불가: 'food' 카테고리를 사용하는 거래가 존재합니다.
      [힌트] 해당 카테고리를 삭제하려면 먼저 사용하는 거래의 카테고리를 변경하거나 --replacement로 대체 카테고리를 지정하세요.

- 7. update --id TX-000001 [--date ...] [--type ...] [--category ...] [--amount ...] [--memo ...] [--tags a,b]
  - 옵션 기반 수정
    python -m budget_app update --id TX-000001 --date 2026-10-25 --type expense --category shopping --amount 42000 --memo "생활용품 구매" --tags home,necessity
      [수정 완료] id=TX-000001

- 8. delete --id TX-000001
  - 거래 삭제
    python -m budget_app delete --id TX-000001
      [삭제 완료] id=TX-000001

- 9. export --out FILE.csv --month YYYY-MM
  - 또는 --from YYYY-MM-DD --to YYYY-MM-DD
    python -m budget_app export --out FILE1.csv --month 2026-10       
      [완료] FILE1.csv (6 records)

- 9. import --from FILE.csv
  - CSV 파일에서 거래 일괄 등록 (스키마 준수 필요)
    python -m budget_app import --from FILE1.csv
      [완료] imported=6, skipped=0

- 10. 추가 조건(최종 결과물의 필수 구성)
  기본 데이터 폴더 및 파일
  - 기본 데이터 폴더: ./data (--data-dir 옵션으로 변경 가능)
  - 저장 파일(영구 저장, JSONL 포맷):
    - ./data/transactions.jsonl
    - ./data/categories.jsonl
    - ./data/budgets.jsonl

  CSV import/export 스키마 (UTF-8, 헤더 포함)
  - 컬럼: date,type,category,amount,memo,tags
  - 예:
    date,type,category,amount,memo,tags
    2024-01-15,expense,food,15000,점심,meal,lunch

설계/구조 요약
- 모듈 분리: cli.py, services.py, storage.py, models.py, decorators.py, utils.py
- 데이터 모델: dataclass 기반 (Transaction, Budget, Category)
- 저장 방식: JSONL 파일을 스트리밍(generator)으로 읽음
- 원자성: update/delete 등 파일 변경 시 임시 파일 작성 후 os.replace로 교체
- 데코레이터: 예외 처리(handle_errors), 실행 시간 로깅(log_time)

오류 처리 및 종료 코드
- 오류 발생 시 스택트레이스 대신 원인/힌트 메시지를 출력하고 비정상 종료(exit code != 0)

추가 메모
- 초기 실행 시 categories.jsonl이 비어 있으면 기본 카테고리 목록을 자동 생성합니다.
- 요구사항에 맞춰 데이터는 transactions/categories/budgets로 분리되어 저장됩니다.

문의
- 개선하거나 추가할 보너스 기능(백업, 반복 거래 자동생성, 출력 표 포맷 개선 등)이 필요하면 알려주세요.
