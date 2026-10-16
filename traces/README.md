# 실행 기록 (traces)

- 파일 하나가 `claude -p --output-format stream-json --verbose` 실행 한 번의 원본이다.
- 이름 규칙: `<작업>__<조건>__r<회차>.jsonl`
  - `control` = 수정 전(before): CLAUDE.md에 UTF-8 규칙이 없다
  - `rule` = 수정 후(after): CLAUDE.md에 UTF-8 규칙 1줄이 있다
- 마지막 줄(`"type":"result"`)에 `num_turns`, `duration_ms`, `usage`, `total_cost_usd`가 있다.
- 사람이 읽기 쉬운 명령 흐름은 아래 명령으로 볼 수 있다.

```
python -X utf8 -I scripts/show_commands.py fix-failing__rule__r1 fix-failing__control__r1
```

비교하기 좋은 한 쌍은 `fix-failing__control__r1`과 `fix-failing__rule__r1`이다. control은 첫 테스트에서 cp949 오류를 본다. rule은 `python -X utf8 test_me.py`로 돌려서 버그가 가려진 채 통과를 본다. 그래도 rule은 코드를 직접 읽고 고쳤다.
