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

저장 포맷 선택 근거: JSONL vs CSV
- 선택 포맷: JSONL
- 이유:
  - 거래/카테고리/예산 데이터는 append 중심의 로그형 저장을 전제로 하므로, 새 레코드를 마지막에 추가하는 JSONL이 간단하고 빠릅니다.
  - 각 레코드가 독립 JSON 객체이므로, `stream()`으로 한 줄씩 읽어 처리할 때 메모리 사용을 줄일 수 있습니다.
  - 거래를 조회/검색/요약하는 흐름에서 전체 파일을 읽더라도, generator 기반으로 순차 접근하는 구조와 잘 맞습니다.
- CSV의 장점:
  - 외부 도구와의 호환성이 좋고, 엑셀/스프레드시트/데이터 분석 도구에 바로 임포트하기 편합니다.
  - 단순한 데이터 교환 시 인간이 읽기 쉽습니다.
- CSV의 단점:
  - append write가 JSONL보다 다루기 불편하고, 큰 파일에서 전체 읽기/필터링 시 오버헤드가 큽니다.
  - 구조적 데이터(태그 배열, 메모 문자열 포함 등)를 그대로 저장하기보다 문자열 변환이 필요합니다.
- 결론:
  - 영속 저장은 JSONL을 선택하고, import/export는 CSV 스키마를 지원해 둘의 장점을 결합했습니다.

대용량 데이터(100k 건) 병목 및 개선 방안
- 예상 병목 지점:
  - `TransactionRepository.all()` 또는 전체 스캔형 검색은 거래 수가 증가할수록 O(n) 비용이 커집니다.
  - ID 생성 시 `stream()`으로 전체 파일을 순회해 최대 값을 찾는 로직은, 거래 건수가 많을수록 추가 비용이 발생합니다.
  - `category remove`와 같은 작업은 관련 거래를 순회해 카테고리 사용 여부를 확인해야 하므로 비용이 증가합니다.
- 개선 방안:
  1. 인덱스 파일 추가: `id -> offset` 또는 월별/카테고리별 인덱스를 두어 검색 범위를 줄이고 전체 파일 스캔을 최소화합니다.
  2. 배치 처리/청크 단위 로딩: 대량 import/export 시 전체 데이터를 한 번에 읽지 않고 일정 크기씩 나눠 처리합니다.
  3. SQLite 또는 경량 DB 전환: 집계/검색/업데이트가 잦아지면 JSONL 기반 구조보다 인덱스와 트랜잭션 지원이 더 유리합니다.
  4. 추가 최적화: `id` 생성 시 파일 끝의 마지막 ID를 메모리에 캐시하거나, 더 빠른 해시 기반 인덱스를 두는 방식을 고려할 수 있습니다.
- 현재 설계의 한계:
  - JSONL은 append와 스트리밍에 강점이 있지만, 다수 조건 검색이나 대용량 집계에서는 인덱스와 DB 전환이 더 유리합니다.

CSV import 처리 정책
- 현재 구현 정책: 부분 성공(partial import) 방식
  - CSV 파일을 한 줄씩 읽어 `DictReader`로 파싱합니다.
  - 유효하지 않은 행(날짜 형식 오류, 타입 오류, 금액 비정상, 미등록 카테고리 등)은 건너뛰고 `skipped` 카운트를 증가시킵니다.
  - 정상 행만 저장되며, 최종 출력은 `imported={N}, skipped={M}` 형태로 확인할 수 있습니다.
- 장점:
  - 깨진 행 하나 때문에 전체 import가 멈추지 않고, 나머지 정상 데이터는 계속 저장됩니다.
  - 사용자가 어떤 비율로 처리되었는지 빠르게 파악할 수 있습니다.
- 현재 한계:
  - 전체 트랜잭션 롤백(all-or-nothing)은 지원하지 않습니다.
  - 실패 행에 대한 세부 사유(행 번호, 오류 원인)와 리포트 파일 작성 기능은 아직 제한적입니다.
- 향후 개선안:
  - `row_no`, `reason` 컬럼을 가진 실패 리포트 파일 생성
  - `--strict` 옵션으로 실패 시 전체 import 롤백 기능 추가
  - import 전후 로그 파일을 남겨 원인 추적 가능하게 개선
