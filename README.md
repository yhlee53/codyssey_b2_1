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
- add
  - 대화형으로 거래 추가 (date, type, category, amount, memo, tags)
- list --limit N
  - 최신순 거래 출력 (기본 limit=10)
- search --from YYYY-MM-DD --to YYYY-MM-DD --category NAME --type income|expense --q KEYWORD --tag TAG
  - 조건 기반 검색
- update --id TX-000001 [--date ...] [--type ...] [--category ...] [--amount ...] [--memo ...] [--tags a,b]
  - 옵션 기반 수정
- delete --id TX-000001
  - 거래 삭제
- category add | list | remove --name NAME [--replacement NAME]
  - 카테고리 관리 (삭제 시 사용 중이면 replacement로 대체하거나 삭제 차단)
- budget set --month YYYY-MM --amount AMOUNT
  - 월 예산 설정
- summary --month YYYY-MM --top N
  - 월별 요약 (총수입/총지출/잔액 + 카테고리별 지출 TOP N), 예산 사용률/초과 표시
- export --out FILE.csv --month YYYY-MM
  - 또는 --from YYYY-MM-DD --to YYYY-MM-DD
- import --from FILE.csv
  - CSV 파일에서 거래 일괄 등록 (스키마 준수 필요)

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
