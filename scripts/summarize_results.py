"""results/runs.jsonl을 모아 결과 표와 사전 판정식 결과를 results/summary.md에 쓴다."""
import json
import pathlib
import statistics as st
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import REPO, TASKS

rows = [json.loads(l) for l in (REPO / "results" / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
# 같은 run_id가 다시 돌려졌으면 마지막 것만 쓴다
by_id = {}
for r in rows:
    by_id[r["run_id"]] = r
rows = list(by_id.values())


def tok(r):
    return sum((r.get(k) or 0) for k in ("input_tokens", "cache_creation", "cache_read", "output_tokens"))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 1) if xs else None


out = ["# 결과 요약 (자동 생성: scripts/summarize_results.py)", "",
       "## 실행별 기록", "",
       "| run_id | 통과 | 인코딩 오류 | 턴 | 시간(초) | 토큰 | 비용($) | 편집 | `-X utf8` 실행 | 승인 거부 |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: (TASKS.index(r["task"]), r["cond"], r["rep"])):
    out.append(f"| {r['run_id']} | {'O' if r['passed'] else 'X'} | {r['enc_errors']} | {r['num_turns']} | "
               f"{round((r['duration_ms'] or 0) / 1000, 1)} | {tok(r):,} | {r['cost_usd']:.3f} | {r['edits']} | "
               f"{r['python_runs_with_X_utf8']} | {r['permission_denials']} |")

out += ["", "## 작업 × 조건 집계 (3회)", "",
        "| 작업 | 조건 | 통과 | 인코딩 오류 합 | 평균 턴 | 평균 시간(초) | 평균 토큰 | 평균 비용($) | 평균 편집 |",
        "|---|---|---|---|---|---|---|---|---|"]
agg = {}
for t in TASKS:
    for c in ("rule", "control"):
        g = [r for r in rows if r["task"] == t and r["cond"] == c]
        a = {"n": len(g), "pass": sum(r["passed"] for r in g), "enc": sum(r["enc_errors"] for r in g),
             "turns": mean([r["num_turns"] for r in g]), "sec": mean([(r["duration_ms"] or 0) / 1000 for r in g]),
             "tok": mean([tok(r) for r in g]), "cost": mean([r["cost_usd"] for r in g]),
             "edits": mean([r["edits"] for r in g])}
        agg[(t, c)] = a
        out.append(f"| {t} | {c} | {a['pass']}/{a['n']} | {a['enc']} | {a['turns']} | {a['sec']} | "
                   f"{a['tok']:,} | {a['cost']} | {a['edits']} |")

# 사전 판정식 (preregistration.md 4절)
wins = [t for t in TASKS if agg[(t, "rule")]["enc"] < agg[(t, "control")]["enc"]
        and agg[(t, "rule")]["turns"] <= agg[(t, "control")]["turns"]]
pass_rule = sum(agg[(t, "rule")]["pass"] for t in TASKS)
pass_ctrl = sum(agg[(t, "control")]["pass"] for t in TASKS)
ctrl_enc = sum(agg[(t, "control")]["enc"] for t in TASKS)
c1, c2 = len(wins) >= 2, pass_rule >= pass_ctrl
if ctrl_enc == 0:
    verdict = "기각 (불편 미재현: control 조건 인코딩 오류 0)"
else:
    verdict = "지지" if (c1 and c2) else "기각"
tok_rule = mean([tok(r) for r in rows if r["cond"] == "rule"])
tok_ctrl = mean([tok(r) for r in rows if r["cond"] == "control"])
out += ["", "## 사전 판정식 적용", "",
        f"- 조건 1 (2개 이상 작업에서 인코딩 오류 합 감소 + 평균 턴 같거나 감소): 해당 작업 {wins} → {'충족' if c1 else '미충족'}",
        f"- 조건 2 (통과 수 rule ≥ control): rule {pass_rule}/9, control {pass_ctrl}/9 → {'충족' if c2 else '미충족'}",
        f"- control 인코딩 오류 총합: {ctrl_enc}",
        f"- 평균 토큰: rule {tok_rule:,} / control {tok_ctrl:,} ({(tok_rule / tok_ctrl - 1) * 100:+.1f}%)",
        f"- **판정: {verdict}**", ""]
(REPO / "results" / "summary.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
