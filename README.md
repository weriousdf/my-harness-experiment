# my-harness-experiment

Claude Code의 메모리(CLAUDE.md)에 넣은 UTF-8 규칙 한 줄이, Windows(cp949)에서 한글 파일을 다루는 파이썬 작업의 인코딩 오류 왕복을 줄이는지 실험했다. 전체 보고서는 [`experiment-01.md`](experiment-01.md)에 있다.

## 한 줄 결론

**기각.** Sonnet 5.5는 규칙이 없어도 처음부터 `encoding="utf-8"`을 넣었다. 스스로 만든 인코딩 오류는 18회 중 0회였다. 규칙은 행동을 바꿨지만(rule 9회 모두 `python -X utf8` 사용), 결과는 낫게 하지 못했다. 오히려 기존 버그를 테스트에서 가리는 부작용 가능성을 보였다.

## 가설

> CLAUDE.md에 UTF-8 규칙 한 줄을 넣으면, 같은 작업에서 인코딩 오류 발생 수와 턴 수가 줄고, 해결률은 떨어지지 않는다.

## 실험 설계

| 구분 | 내용 |
|---|---|
| 고정 | Claude Code 2.1.278, `claude-sonnet-5-5`, `claude -p`, 작업 3개(fixture 해시 고정), 요청문, 허용 도구, Python 3.14.6, cp949. 전역 CLAUDE.md, 자동 메모리, 전역 env(`PYTHONUTF8`), MCP는 뺐다 |
| 조작 | 작업 폴더 CLAUDE.md에 UTF-8 규칙 1줄이 있음(rule) / 없음(control). 두 조건 모두 같은 무관한 규칙 3줄을 갖는다 |
| 측정 | 해결률(UTF-8 모드를 끈 python으로 채점) + 인코딩 오류 수, 턴, 시간, 토큰, 비용, 편집 수, 승인 거부 수 |
| 반복 | 3작업 × 2조건 × 3회 = 18회, 순서 교차 |
| 반론 통제 | 대조에도 같은 형식의 CLAUDE.md를 둔다. 전역 env를 뺀다. 3회 반복한다. Claude 밖에서 따로 채점한다 |
| 사전 판정식 | 2개 이상 작업에서 rule의 인코딩 오류 합이 적고 평균 턴이 같거나 적으며, 통과 수가 rule ≥ control이면 지지. 그 밖은 기각. 실행 전에 [`preregistration.md`](preregistration.md)로 커밋했다(`e968075`) |

## 결과

| 작업 | rule 통과 / 오류 합 / 평균 턴 | control 통과 / 오류 합 / 평균 턴 |
|---|---|---|
| parse-log | 3/3 · 0 · 6.0 | 3/3 · 0 · 6.0 |
| csv-summary | 3/3 · 0 · 5.3 | 3/3 · 0 · 6.3 |
| fix-failing | 3/3 · 0 · 7.0 | 3/3 · 3 · 6.3 |

- 판정식 ①은 충족한 작업이 0개라 미충족이다. fix-failing은 오류는 줄었지만 턴이 늘었다.
- 판정식 ②는 9/9 대 9/9로 충족이다.
- 그래서 판정은 **기각**이다.
- fix-failing control의 오류 3건은 작업이 원래 보여 주는 버그였다. rule의 0건은 `-X utf8` 실행이 버그를 가린 결과였다(보고서 5-3절).

## 다시 검토할 조건

- 모델을 바꿨는데 스스로 만든 인코딩 오류가 다시 나타날 때
- 실제 업무에서 인코딩 왕복을 다시 관찰했을 때. 그 입력은 fixture에 추가한다
- Python 3.15 이상(UTF-8 기본)으로 올릴 때
- 반복을 10회 이상으로 늘려 턴 수 차이가 일관되게 나올 때

다음 실험(안)은 settings.json env `PYTHONUTF8`을 조작 변인으로 삼는다. 작업에는 PowerShell 5.1 한 줄 파이썬과 콘솔 출력을 더한다.

## 폴더

```
my-harness-experiment/
├── README.md            # 이 요약
├── experiment-01.md     # 전체 보고서
├── preregistration.md   # 실행 전에 커밋한 설계·판정식
├── traces/              # 실행 18회의 stream-json 원본 (control = 수정 전, rule = 수정 후)
├── fixture/             # 고정 입력 원본(작업 3개, 조건별 CLAUDE.md, 요청문, 해시)
├── results/             # runs.jsonl(실행별 수치), summary.md(집계)
└── scripts/             # 실행기, 채점, 격리 확인, 집계
```

## 다시 돌리는 법

Windows, Claude Code 로그인 상태에서 실행한다.

```
python -X utf8 -I scripts/check_fixture.py      # fixture 점검
python -X utf8 -I scripts/run_experiment.py     # 18회 실행 (끝난 것은 건너뜀)
python -X utf8 -I scripts/summarize_results.py  # 집계와 판정
```

`scripts/common.py`의 `RUNS` 경로와, `run_experiment.py`의 `claudeMdExcludes` 경로(사용자 전역 CLAUDE.md 위치)는 자기 PC에 맞게 바꿔야 한다.
