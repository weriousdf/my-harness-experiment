# 사전 등록: 실험 설계와 판정식

이 파일은 실험을 실행하기 **전에** 커밋한다. 커밋 시각이 결과보다 앞선다는 것이 "결과를 보고 기준을 바꾸지 않았다"는 근거다. 실행 뒤에는 이 파일을 고치지 않는다.

## 1. 불편 (1단계)

- 작업: Windows 11 한국어 PC에서 Claude Code에 한글이 든 파일(로그·CSV·명단)을 다루는 파이썬 스크립트를 만들거나 고치게 했다.
- 입력 뒤 일어난 일: Claude가 `open()`에 인코딩을 지정하지 않은 코드를 쓴다. 실행하면 `UnicodeDecodeError: 'cp949' codec can't decode`가 난다. Claude는 그 뒤에야 `encoding="utf-8"`을 넣고 다시 실행한다. 이 왕복이 작업마다 되풀이되어 턴과 시간이 늘었다.
- 사용자는 2026-10-10 전역 CLAUDE.md에 "처음부터 UTF-8로 한다" 규칙을 넣었다. 그 뒤 나아졌다는 느낌은 있지만, 측정한 적은 없다.
- 하네스 탓인지 의심할 점: 원인은 Windows 로케일 인코딩(cp949)과 Python 3.14 이하의 기본값일 수 있다. 모델의 습관일 수도 있다. 하네스(Claude Code)는 원인이 아니라 완화 수단일 수 있다.

## 2. 가설 (2단계)

> Claude Code의 프로젝트 메모리(CLAUDE.md)에 UTF-8 규칙 한 줄을 넣으면, 같은 작업에서 인코딩 오류 발생 수와 턴 수가 줄고, 해결률은 떨어지지 않는다.

반증 조건: 규칙이 있는 조건에서 인코딩 오류나 턴 수가 줄지 않거나, 해결률이 떨어지면 가설은 틀렸다.

## 3. 실험 설계 (3단계)

| 구분 | 내용 |
|---|---|
| 고정 | Claude Code 2.1.278, 모델 `claude-sonnet-5-5`, `claude -p` 비대화 실행, 작업 3개(fixture 원본 고정, `fixture/MANIFEST.json` 해시), 같은 요청문(`fixture/prompts.json`), 허용 도구 목록, `--max-turns 40`, 실행당 시간 한도 900초, Python 3.14.6, 로케일 cp949 |
| 격리 | 사용자 전역 CLAUDE.md는 `claudeMdExcludes`로 뺐다. 자동 메모리는 껐다. 사용자 settings.json은 `--setting-sources project,local`로 빼서, 그 안의 env `PYTHONUTF8=1`이 들어가지 않는다. MCP는 `--strict-mcp-config`로 막았다. 실행마다 새 세션을 쓰고(`--no-session-persistence`), 실행마다 fixture를 새로 복사했다. 확인은 `scripts/probe_isolation.py`로 했다 |
| 조작 (하나만) | 메모리 표현: 작업 폴더의 CLAUDE.md. **rule** 조건 = 무관한 규칙 3줄 + UTF-8 규칙 1줄(`fixture/conditions/rule_CLAUDE.md`). **control** 조건 = 무관한 규칙 3줄만(`control_CLAUDE.md`) |
| 반복 | 작업 3 × 조건 2 × 3회 = 18회. 조건 순서는 회차마다 번갈아 둔다 |
| 측정 (이중) | 해결률: 채점 테스트 통과 여부. 채점은 UTF-8 모드를 끈 기본 python으로 한다. 테스트·입력 파일을 고쳤으면 실패로 본다. 비용 쪽: 인코딩 오류 수(도구 결과 중 `UnicodeDecodeError`, `UnicodeEncodeError`, `codec can't decode/encode`, `illegal multibyte`가 든 결과의 개수), 턴 수(`num_turns`), 소요 시간(`duration_ms`), 토큰(입력+캐시 생성+캐시 읽기+출력), 비용(USD), 편집 도구 호출 수, 승인 거부 수(`permission_denials`) |

### 작업 3개

| 작업 | 입력 | 요청 | 확인 |
|---|---|---|---|
| parse-log | `sample.log`(UTF-8, 한글, em dash) | ERROR 줄을 마크다운 표로 만들어 `errors.md`에 저장하는 `parse.py`를 만든다 | `test_parse.py` |
| csv-summary | `sales.csv`(UTF-8, 한글) | 지역별 합계를 `summary.json`에 한글 그대로 저장하는 `summarize.py`를 만든다 | `test_summary.py` |
| fix-failing | `report.py`(인코딩 미지정), `names.txt` | 실패 2건이 통과하도록 `report.py`를 고친다 | `test_me.py` |

fixture 점검(`scripts/check_fixture.py`) 결과는 다음과 같다. 원본 그대로는 세 작업 모두 실패한다. 인코딩을 빼먹은 해답도 실패한다. UTF-8을 명시한 해답만 통과한다.

### 예상 반론과 통제

| 반론 | 통제 |
|---|---|
| 효과는 규칙 내용이 아니라 CLAUDE.md가 있거나 길어진 것 자체에서 온다 | 대조 조건에도 같은 형식의 CLAUDE.md(무관한 규칙 3줄)를 둔다. 두 조건의 차이는 UTF-8 규칙 1줄뿐이다 |
| 원래 불편은 하네스가 아니라 Windows·Python 기본값 탓이다. 또는 전역 설정의 `PYTHONUTF8`가 이미 해결하고 있었다 | 전역 env를 뺀 상태에서 대조 조건에 오류가 나는지 본다(불편 재현 여부). 재현되지 않으면 그대로 보고한다 |
| 모델 출력은 무작위라서, 한 번 결과로는 우연과 구별할 수 없다 | 3회 반복하고, 순서를 번갈아 둔다. 표본이 작다는 점은 결과에 그대로 적는다 |
| 규칙의 "`python -X utf8`로 실행"이 Claude 쪽 테스트에서 버그를 가린다(코드는 틀렸는데 통과하는 것처럼 보임) | 채점은 Claude 밖에서 UTF-8 모드를 끈 기본 python으로 따로 한다. 실행 기록에서 `-X utf8` 사용 횟수도 센다 |

## 4. 사전 판정식

작업별로 3회의 값을 모은다. 인코딩 오류는 합계로, 턴 수는 평균으로, 통과는 개수로 본다.

**가설 지지**: 아래 두 가지를 모두 만족할 때.

1. 세 작업 가운데 **2개 이상**에서 rule 조건이 control 조건보다 인코딩 오류 합계가 **적고**, 평균 턴 수가 **같거나 적다**.
2. 전체 통과 수가 rule ≥ control이다(각 9회 중).

**가설 기각**: 그 밖의 모든 경우.

추가로 미리 정해 두는 해석 규칙은 다음과 같다.

- control 조건의 인코딩 오류가 세 작업 모두에서 0이면, 판정은 **기각(불편 미재현)**으로 적는다. 이 경우 불편의 원인은 이 환경에서 하네스 메모리가 아닌 다른 것(예: 전역 env, 모델 변화)으로 해석한다.
- 시간·토큰·비용은 판정에 쓰지 않는다. 보고만 한다. 다만 rule 조건의 평균 토큰이 control보다 20% 넘게 많으면, "효과가 있더라도 비용이 든다"고 따로 적는다. 20%는 Gloaguen et al.(2026)이 보고한 컨텍스트 파일의 비용 증가 폭에서 따왔다.
- 시간 한도를 넘긴 실행은 실패로 센다. 실행기 오류(Claude가 시작되지 않음)는 같은 조건으로 한 번 다시 돌린다. 다시 돌린 사실은 보고서에 적는다.
