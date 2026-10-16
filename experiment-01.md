# 실험 01: CLAUDE.md의 UTF-8 규칙은 Windows 인코딩 오류 왕복을 줄이는가

- 실험자: 김보겸 (실험 설계·실행 보조: Claude Code, Opus 5.5)
- 실행일: 2026-10-16
- 사전 등록: [`preregistration.md`](preregistration.md) — 실행 전에 커밋 `e968075`로 올렸다

## 1. 불편과 가설

### 1-1. 고른 불편

나는 Windows 11 한국어 PC에서 Claude Code로 업무 자료(엑셀에서 뽑은 CSV, 로그, 한글 명단)를 다룬다. Claude는 한글 파일을 읽고 쓰는 파이썬 스크립트를 자주 만들었다. 그때마다 같은 장면이 되풀이됐다.

1. Claude가 `open(path)`처럼 인코딩을 지정하지 않은 코드를 쓴다.
2. 실행하면 `UnicodeDecodeError: 'cp949' codec can't decode byte ...`가 난다.
3. Claude가 `encoding="utf-8"`을 넣고 다시 실행한다. 출력에서 한글이 깨져 한 번 더 고치기도 한다.

작업 하나에 1~3턴이 이 왕복에 쓰였다. 그래서 2026-10-10에 전역 CLAUDE.md에 "모든 작업은 처음부터 UTF-8로 한다" 규칙을 넣었다. 같은 무렵 전역 settings.json의 env에 `PYTHONUTF8=1`도 넣었다. 그 뒤 나아졌다는 느낌은 있었지만, 측정한 적은 없다. **두 조치 중 무엇이 효과를 냈는지도 모른다.**

### 1-2. 이 불편이 하네스 탓인지에 대한 의심

| 후보 원인 | 하네스 기능인가 | 이번 실험에서 다루는 방법 |
|---|---|---|
| Windows 로케일 인코딩(cp949)과 Python 3.14의 기본값. PEP 686에 따르면 UTF-8 모드는 3.15부터 기본이다 | 아니다 (OS·언어) | 고정한다. 실험 PC에서 UTF-8 모드는 0, 기본 인코딩은 `cp949`로 확인했다 |
| 모델의 습관(인코딩 인자를 생략함) | 아니다 (모델) | 모델을 고정한다. 대조 조건의 오류 발생률로 기저 수준을 잰다 |
| 메모리(CLAUDE.md)에 환경 정보가 없음 | **그렇다** | 조작 변인으로 삼는다 |
| 하네스 설정의 env(`PYTHONUTF8`) | 그렇다 (다른 기능) | 실험에서는 뺀다. 다음 실험 후보로 남긴다 |
| 내 요청 문장이 인코딩을 말하지 않음 | 아니다 (사용자) | 요청문을 고정한다(`fixture/prompts.json`) |

### 1-3. 가설

> Claude Code의 프로젝트 메모리(CLAUDE.md)에 UTF-8 규칙 한 줄을 넣으면, 같은 작업에서 인코딩 오류 발생 수와 턴 수가 줄고, 해결률은 떨어지지 않는다.

이 가설은 반증할 수 있다. 규칙이 있는 조건에서 인코딩 오류나 턴 수가 줄지 않거나, 해결률이 떨어지면 틀린 것이 된다.

### 1-4. 도구 선택 이유

Claude Code를 골랐다. 이유는 셋이다.

- 실제로 매일 쓰는 도구이고, 불편도 여기서 겪었다.
- 메모리 표현(CLAUDE.md)을 파일 하나로 바꿀 수 있다. 이 PC에서 실제로 조작할 수 있는 항목이다.
- `claude -p --output-format stream-json`으로 실행 기록(trace)과 턴·토큰·시간을 기계적으로 남길 수 있다.

## 2. 배경 근거

근거 종류 표기: [학술] = 논문(arXiv·학회), [벤더] = 도구 회사의 자체 글, [공식 문서] = 제품·언어 공식 문서. 벤더 글은 독립 비교가 아니라 자기 제품에 대한 설명이므로, 수치 근거로 쓰지 않는다.

| # | 출처 | 종류 | 이 실험과 관련된 내용 | 그 연구가 검증하지 않은 것 |
|---|---|---|---|---|
| 1 | Lulla et al., *On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents*, ICSE JAWs 2026, [arXiv:2601.20404](https://arxiv.org/abs/2601.20404) | [학술] | 저장소 10개, PR 124건. Codex CLI(gpt-5.2-codex)에서 AGENTS.md가 있으면 실행 시간 중앙값이 98.57초에서 70.34초로 줄었다(원문: "a lower median runtime (Δ 28.64%)"). 출력 토큰은 16.58% 줄었고, 입력 토큰은 1~3% 늘었다 | 에이전트·모델이 하나뿐이다. 정답 여부는 평가하지 않았다. 인과가 아닌 연관이다. Windows·인코딩은 다루지 않았다 |
| 2 | Gloaguen et al. (ETH Zurich), *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*, 2026, [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) | [학술] | Claude Code(Sonnet-4.5) 등 네 에이전트로 시험했다. 원문: "providing context files does not generally improve task success rates". LLM이 만든 파일은 비용이 약 20% 늘었고, 개발자가 쓴 파일은 해결률 +2.4%(유의하지 않음)였다. 비표준 관행을 알려 주는 데는 쓸모가 있다고 보고했다 | Python 저장소만, Linux Docker 환경에서만 시험했다. Windows·cp949와 인코딩 오류 재시도는 따로 재지 않았다 |
| 3 | Jaroslawicz et al., *How Many Instructions Can LLMs Follow at Once?* (IFScale), 2025, [arXiv:2507.11538](https://arxiv.org/abs/2507.11538) | [학술] | 지시가 많아질수록 지키는 비율이 떨어진다. 지시 500개에서는 최고 모델도 약 68%였다. 앞쪽 지시를 더 잘 지키는 경향도 있었다. 이번 실험의 규칙은 4줄이라 이 문제에서 먼 조건이다 | 코딩 에이전트가 아니다. 지시가 키워드 포함 형태뿐이다. 원문을 직접 확인하지 못해 수치는 검색 요약 기준이다(미확인 표시) |
| 4 | Shinn et al., *Reflexion*, NeurIPS 2023 ([arXiv:2303.11366](https://arxiv.org/abs/2303.11366)); Zhao et al., *ExpeL*, AAAI 2024 ([arXiv:2308.10144](https://arxiv.org/abs/2308.10144)) | [학술] | 실패 경험을 말로 정리해 다음 시도에 넣으면 성능이 오른다는 방향의 연구다. 내 UTF-8 규칙도 "지난 실패를 한 줄 규칙으로 남긴 것"이라 같은 계열이다 | 경험을 영구 파일로 저장하는 방식이 아니다. CLI 에이전트도 Windows도 아니다. 이번에 수치를 다시 확인하지 않았다 |
| 5 | Anthropic, *How Claude remembers your project*, [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) | [공식 문서] | CLAUDE.md는 세션 시작 때 읽힌다. 원문: "Claude treats them as context, not enforced configuration." 즉 지켜진다는 보장이 없다. 반드시 지켜야 하는 동작은 hook을 쓰라고 안내한다 | 정량 근거가 없다(사용 안내) |
| 6 | Anthropic, *Effective context engineering for AI agents*, 2025-09-29, [anthropic.com/engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | [벤더] | CLAUDE.md는 처음부터 컨텍스트에 그대로 들어간다. 컨텍스트는 한정된 자원이라고 설명한다 | 수치 실험이 없다. 자기 제품에 대한 벤더의 설명이다 |
| 7 | Python, *PEP 686 – Make UTF-8 mode default*, [peps.python.org/pep-0686](https://peps.python.org/pep-0686/) | [공식 문서] | 인코딩 인자를 빠뜨리면 플랫폼마다 결과가 다르다. 원문: "So this change mostly affects Windows users." UTF-8 모드는 3.15부터 기본값이다 | cp949를 직접 언급하지 않는다. 그래서 실험 PC의 실측값(`cp949`)을 따로 근거로 쓴다 |

근거 정리:

- 1·2는 같은 질문(저장소 지시 파일이 에이전트를 돕는가)에 다른 답을 냈다. 1은 시간이 줄었다고 했고, 2는 해결률은 그대로이고 비용만 늘었다고 했다. 그러니 "CLAUDE.md는 도움이 된다"는 일반론을 내 환경에 그대로 쓸 수 없다.
- 2가 "비표준 관행에는 쓸모가 있다"고 한 점이 내 가설과 가장 가깝다. Windows cp949 환경에서 UTF-8을 명시하라는 규칙은 모델이 저장소만 보고는 알 수 없는 환경 정보이기 때문이다.
- Windows·cp949·인코딩 오류 재시도를 측정한 연구는 찾지 못했다. 이 실험은 그 빈칸을 내 환경 한 곳에서 확인하는 것이다.

## 3. 실험 설계

전체 설계는 [`preregistration.md`](preregistration.md)에 실행 전에 적어 두었다. 요약은 다음과 같다.

| 구분 | 내용 |
|---|---|
| 고정 | Claude Code 2.1.278, `claude-sonnet-5-5`, `claude -p` 비대화 실행, 작업 3개(fixture 해시 고정), 같은 요청문, 같은 허용 도구, `--max-turns 40`, 실행당 900초 한도, Python 3.14.6, 로케일 cp949. 사용자 전역 CLAUDE.md, 자동 메모리, 전역 env, MCP는 뺐다 |
| 조작 (하나만) | 작업 폴더 CLAUDE.md의 UTF-8 규칙 1줄이 있느냐(rule) 없느냐(control). 두 조건 모두 같은 무관한 규칙 3줄을 갖는다 |
| 측정 (이중) | 해결률(채점 테스트 통과)과 함께 인코딩 오류 수, 턴 수, 시간, 토큰, 비용, 편집 횟수, 승인 거부 수 |
| 반복 | 작업 3 × 조건 2 × 3회 = 18회, 조건 순서는 회차마다 번갈아 둠 |
| 반론 | ① 효과는 규칙 내용이 아니라 CLAUDE.md가 있는 것 자체에서 온다 → 대조에도 같은 형식의 CLAUDE.md를 둔다. ② 원인은 OS·Python 기본값이나 전역 env다 → env를 빼고, 대조 조건에서 불편이 재현되는지 본다. ③ 모델 출력의 무작위성 → 3회 반복하고 순서를 교차한다. ④ 규칙의 `-X utf8` 실행이 버그를 가린다 → Claude 밖에서 UTF-8 모드를 끈 python으로 채점한다 |
| 사전 판정식 | **지지** = 세 작업 중 2개 이상에서 rule이 control보다 인코딩 오류 합이 적고 평균 턴이 같거나 적다. 그리고 전체 통과 수가 rule ≥ control이다. **그 밖은 기각**이다. control의 인코딩 오류가 전부 0이면 "기각(불편 미재현)"으로 적는다 |

격리 확인(`scripts/probe_isolation.py`)도 했다. 처음에는 `--setting-sources project,local`만 썼는데, 전역 CLAUDE.md와 자동 메모리가 여전히 읽혔다. 하위 Claude가 사용자 이름을 알고 있었다. 그래서 `claudeMdExcludes`와 자동 메모리 끄기를 더했다. 그 뒤에는 사용자 정보와 인코딩 관련 지시가 모두 보이지 않았다. 하위 Claude가 실행한 python도 `utf8_mode=0`, `PYTHONUTF8=None`, `cp949`로 나왔다. 이 과정 자체가 하네스에 대한 관찰이다. 설정 출처를 고르는 옵션이 메모리 출처까지 고르지는 않는다.

## 4. 실행 기록

- 18회를 모두 실행했다(2026-10-16). 실행기 오류나 시간 초과는 없었다. 그래서 다시 돌린 실행도 없다.
- 실행 기록: [`traces/`](traces/)에 실행마다 `stream-json` 원본 한 개(`<작업>__<조건>__r<회차>.jsonl`)가 있다. 수정 전(before)은 `control`, 수정 후(after)는 `rule` 조건이다. 안내는 [`traces/README.md`](traces/README.md)에 있다.
- 실행별 수치: [`results/runs.jsonl`](results/runs.jsonl). 집계는 [`results/summary.md`](results/summary.md)이고, `scripts/summarize_results.py`로 만들었다.
- 명령 흐름 보기: `python -X utf8 -I scripts/show_commands.py <run_id>`

## 5. 결과와 판정

### 5-1. 작업 × 조건 집계 (각 3회)

| 작업 | 조건 | 통과 | 인코딩 오류 합 | 평균 턴 | 평균 시간(초) | 평균 토큰 | 편집 | `-X utf8` 실행 |
|---|---|---|---|---|---|---|---|---|
| parse-log | rule | 3/3 | 0 | 6.0 | 13.1 | 119,612 | 1 | 3회 |
| parse-log | control | 3/3 | 0 | 6.0 | 13.6 | 131,474 | 1 | 0회 |
| csv-summary | rule | 3/3 | 0 | 5.3 | 12.7 | 142,751 | 1 | 3회 |
| csv-summary | control | 3/3 | 0 | 6.3 | 14.6 | 169,692 | 1 | 0회 |
| fix-failing | rule | 3/3 | 0 | 7.0 | 14.8 | 170,697 | 2 | 5회 |
| fix-failing | control | 3/3 | 3 | 6.3 | 14.8 | 184,027 | 2 | 0회 |

- 승인 거부는 18회 모두 0이었다. 허용 도구를 미리 정했기 때문이다.
- 토큰은 입력, 캐시 생성, 캐시 읽기, 출력을 더한 값이다. 비용은 첫 실행만 0.47달러였고 나머지는 0.13~0.19달러였다. 첫 실행 때 캐시가 처음 만들어졌기 때문이다.

### 5-2. 사전 판정식 적용

| 판정 조건 | 결과 |
|---|---|
| ① 2개 이상 작업에서 rule의 인코딩 오류 합이 더 적고, 평균 턴이 같거나 적다 | 인코딩 오류가 줄어든 작업은 fix-failing 하나뿐이다. 그 작업도 평균 턴은 rule 7.0, control 6.3으로 rule이 더 많다. 충족한 작업 0개 → **미충족** |
| ② 통과 수 rule ≥ control | 9/9 대 9/9 → 충족 |
| control 인코딩 오류 총합 | 3 (전부 fix-failing) |
| 토큰 20% 넘게 증가했나 | 아니다. rule의 평균 토큰이 10.7% 적었다 |

**판정: 기각.**

### 5-3. 숫자 뒤의 실제 장면

control의 인코딩 오류 3건은 내가 1단계에서 적은 불편이 아니다. 내가 적은 불편은 "Claude가 인코딩 없이 코드를 쓰고, 스스로 오류를 낸 뒤 다시 고치는 왕복"이었다. 3건은 모두 fix-failing의 첫 명령 `python test_me.py`에서 나왔다. 이 작업은 원래 고쳐야 할 버그를 보여 주는 것이 목적이라, 실패가 나오는 것이 정상이다.

반대로 rule의 0건은 오류를 막은 결과가 아니다. 규칙에 따라 Claude가 테스트를 `python -X utf8 test_me.py`로 돌렸고, 그러자 버그가 있는데도 테스트가 통과했다. Claude는 그 뒤 코드를 직접 읽고 `encoding="utf-8"`을 넣었다. 그래서 채점(UTF-8 모드를 끈 python)도 통과했다. 사전에 적은 반론 ④("규칙이 버그를 가린다")가 실제로 일어난 것이다. 이번에는 Claude가 코드를 읽어서 피해가 없었을 뿐이다.

내가 걱정한 "스스로 만든 인코딩 오류"는 **18회 중 0회**였다. parse-log와 csv-summary의 control 조건에서도 Claude는 처음부터 `encoding="utf-8"`을 넣었다. csv에는 `utf-8-sig`까지 썼다. 즉 이 모델과 이 작업에서는 규칙이 해결할 불편이 처음부터 없었다.

## 6. 돌아보기: 불편의 원인은 하네스 기능(메모리)이었나

**결론부터 적는다.** 이번 실험으로는 "메모리에 규칙이 없어서 인코딩 오류가 반복됐다"는 설명을 지지할 수 없다. 불편이 재현되지 않았기 때문이다.

확인한 범위:

- Claude Code 2.1.278과 Sonnet 5.5, Python 3.14, cp949 환경에서 확인했다. 전역 설정을 모두 뺀 깨끗한 상태에서, 작은 단일 파일 작업 3종을 각 3회 돌렸다. 이 범위에서 모델은 규칙 없이도 UTF-8을 명시했다.
- 규칙은 행동을 바꿨다. rule 조건 9회 모두가 `-X utf8`을 썼고, control은 한 번도 쓰지 않았다. 공식 문서에 "지켜진다는 보장이 없다"는 말이 있지만, 이번에는 규칙이 실제로 지켜졌다. 그러나 바뀐 행동이 결과(오류·턴)를 낫게 만들지는 못했다. 오히려 테스트 결과를 가리는 부작용 가능성을 보였다.

원인 설명을 약하게 만든 것들:

1. **모델이 다르다.** 불편을 겪던 때는 여러 모델(Opus·Sonnet 예전 판, GPT)을 섞어 썼다. 실험은 Sonnet 5.5 하나로만 했다. 불편이 "예전 모델의 습관"이었다면, 메모리 규칙은 원인이 아니라 그 시기의 우연한 처방이다.
2. **불편이 난 자리가 다르다.** 실제 업무에서 오류가 자주 난 곳은 파이썬 파일 안보다 PowerShell 5.1에서 한 줄 파이썬(`-c`)이나 here-string을 쓰는 자리, 그리고 콘솔 출력이었다. 전역 CLAUDE.md에 "한 줄 넘는 파이썬은 .py로 저장해 실행한다"는 규칙을 따로 둔 이유도 이것이다. fixture는 파일 입출력만 다뤄서 이 경로를 재지 못했다.
3. **두 조치가 섞여 있었다.** 불편이 줄었다고 느낀 시점에 CLAUDE.md 규칙과 settings.json env `PYTHONUTF8=1`을 동시에 넣었다. 실험에서는 env를 뺐다. 그러니 실제 효과가 env에서 왔을 가능성은 이번 실험으로 배제되지 않는다. env는 모델이 규칙을 따르든 말든 강제로 적용된다. 공식 문서도 "꼭 지켜야 할 동작은 설정·hook으로 하라"고 안내한다.
4. **지표가 섞였다.** "인코딩 오류 수"가 "스스로 만든 오류"와 "작업이 원래 보여 주는 오류"를 구분하지 못했다. fix-failing의 control 3건이 바로 후자다. 사전 판정식은 이 둘을 같은 수로 셌다.
5. **표본이 작다.** 조건마다 3회뿐이다. 턴 수 차이(예: csv-summary 5.3 대 6.3)는 1턴 안팎이라, 우연과 구별할 수 없다.

미확인 사항:

- 긴 대화나 여러 파일을 다루는 작업에서 규칙이 쓸모 있는지
- Opus, Haiku, 다른 도구(opencode 등)에서 결과가 같은지
- PowerShell `-c` 경로에서 오류가 나는 빈도
- env `PYTHONUTF8`만으로 같은 효과가 나는지

## 7. 다음 실험 계획과 재검토 조건

**실험 02 (안)**

- 조작: 하네스 설정 env `PYTHONUTF8=1`이 있느냐 없느냐. 메모리 규칙은 양쪽 모두 뺀다.
- 고정: 작업에 "PowerShell 5.1에서 한글을 출력하는 한 줄 파이썬"과 "콘솔에 한글 표를 출력하는 스크립트"를 더한다. 실제 불편이 난 자리를 fixture로 옮기는 것이다. 조건마다 5회 이상 돌린다.
- 지표 정의 수정: 인코딩 오류를 "작업이 원래 보여 주는 오류"와 "Claude가 쓴 코드가 낸 오류"로 나눠 센다. 후자는 Claude가 Write나 Edit로 만든 파일을 실행했을 때 난 오류로 정의한다.
- 반론 ④에 대한 장치: rule 조건에서도 테스트는 기본 python으로 돌리게 하거나, 규칙에서 `-X utf8 실행` 부분을 빼고 "`encoding` 명시"만 남긴 조건을 더한다.

**재검토 조건.** 다음 가운데 하나가 생기면 이 결론(기각)을 다시 본다.

- 모델을 바꿨는데(예: Haiku나 다른 회사 모델) 스스로 만든 인코딩 오류가 다시 나타날 때
- Python 3.15 이상으로 올려 기본값이 UTF-8이 될 때. 이때는 실험 자체가 의미를 잃는다(PEP 686)
- 실제 업무에서 인코딩 왕복을 다시 관찰했을 때. 그때는 그 장면의 입력을 그대로 fixture에 추가한다
- 같은 설계를 조건마다 10회 이상으로 늘렸는데, 턴 수 차이가 일관되게 한쪽으로 나올 때
