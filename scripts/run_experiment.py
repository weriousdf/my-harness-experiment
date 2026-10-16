"""실험 실행기: 작업 3 × 조건 2 × 반복 3 = 18회. 이미 끝난 실행은 건너뛴다.
사용: python -X utf8 -I scripts/run_experiment.py [--dry]"""
import json
import pathlib
import re
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import FIXTURE, REPO, RUNS, TASKS, clean_env, fresh_copy, grade

MODEL = "claude-sonnet-5-5"
REPS = 3
CONDS = {"control": "control_CLAUDE.md", "rule": "rule_CLAUDE.md"}
TIMEOUT = 900
ENC_ERR = re.compile(r"UnicodeDecodeError|UnicodeEncodeError|codec can't (?:de|en)code|illegal multibyte")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

prompts = json.loads((FIXTURE / "prompts.json").read_text(encoding="utf-8"))
TRACES = REPO / "traces"
RESULTS = REPO / "results" / "runs.jsonl"
TRACES.mkdir(exist_ok=True)
RESULTS.parent.mkdir(exist_ok=True)

# 전역 CLAUDE.md·자동 메모리를 빼는 설정 (scripts/probe_isolation.py로 확인)
SETTINGS = RUNS / "_isolation_settings.json"
RUNS.mkdir(parents=True, exist_ok=True)
SETTINGS.write_text(json.dumps({
    "claudeMdExcludes": ["C:/Users/bk_ma/.claude/CLAUDE.md", "C:\\Users\\bk_ma\\.claude\\CLAUDE.md"],
    "autoMemoryEnabled": False}), encoding="utf-8")


def tool_result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def analyze(lines):
    m = {"tool_calls": 0, "edits": 0, "bash_calls": 0, "enc_errors": 0, "tool_errors": 0,
         "python_runs_with_X_utf8": 0, "result": None}
    for ln in lines:
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "tool_use":
                    m["tool_calls"] += 1
                    if b["name"] in EDIT_TOOLS:
                        m["edits"] += 1
                    if b["name"] in ("Bash", "PowerShell"):
                        m["bash_calls"] += 1
                        if "-X utf8" in b.get("input", {}).get("command", ""):
                            m["python_runs_with_X_utf8"] += 1
        elif ev.get("type") == "user":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        t = tool_result_text(b)
                        if ENC_ERR.search(t):
                            m["enc_errors"] += 1
                        if b.get("is_error"):
                            m["tool_errors"] += 1
        elif ev.get("type") == "result":
            m["result"] = ev
    return m


def done_ids():
    if not RESULTS.exists():
        return set()
    return {json.loads(l)["run_id"] for l in RESULTS.read_text(encoding="utf-8").splitlines() if l.strip()}


def run_one(task, cond, rep):
    run_id = f"{task}__{cond}__r{rep}"
    wd = RUNS / run_id
    fresh_copy(task, wd, CONDS[cond])
    cmd = ["claude", "-p", prompts[task]["prompt"], "--model", MODEL,
           "--setting-sources", "project,local", "--settings", str(SETTINGS), "--strict-mcp-config",
           "--allowedTools", "Bash", "PowerShell", "Read", "Write", "Edit", "Glob", "Grep",
           "--disallowedTools", "WebFetch", "WebSearch", "Agent",
           "--permission-mode", "acceptEdits", "--max-turns", "40",
           "--output-format", "stream-json", "--verbose", "--no-session-persistence"]
    env = clean_env()
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, encoding="utf-8", timeout=TIMEOUT)
        out, timed_out = r.stdout, False
    except subprocess.TimeoutExpired as e:
        out, timed_out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), True
    wall = round(time.time() - t0, 1)
    (TRACES / f"{run_id}.jsonl").write_text(out, encoding="utf-8")
    m = analyze(out.splitlines())
    res = m.pop("result") or {}
    u = res.get("usage", {})
    g = grade(wd, prompts[task]["test"])
    row = {"run_id": run_id, "task": task, "cond": cond, "rep": rep, "model": MODEL,
           "passed": g["passed"], "tampered": g["tampered"], "timed_out": timed_out,
           "wall_s": wall, "duration_ms": res.get("duration_ms"), "num_turns": res.get("num_turns"),
           "input_tokens": u.get("input_tokens"), "cache_creation": u.get("cache_creation_input_tokens"),
           "cache_read": u.get("cache_read_input_tokens"), "output_tokens": u.get("output_tokens"),
           "cost_usd": res.get("total_cost_usd"), "permission_denials": len(res.get("permission_denials", []) or []),
           "is_error": res.get("is_error"), **m, "grade_tail": g["output_tail"][-400:]}
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(run_id, "passed" if row["passed"] else "FAILED", f"turns={row['num_turns']} enc={row['enc_errors']} "
          f"t={wall}s ${row['cost_usd']}", flush=True)


def main():
    order = []
    for rep in range(1, REPS + 1):
        for task in TASKS:
            conds = ["control", "rule"] if rep % 2 else ["rule", "control"]  # 순서 효과를 줄이려고 번갈아
            order += [(task, c, rep) for c in conds]
    skip = done_ids()
    if "--dry" in sys.argv:
        for o in order:
            print(o, "skip" if f"{o[0]}__{o[1]}__r{o[2]}" in skip else "")
        return
    for task, cond, rep in order:
        if f"{task}__{cond}__r{rep}" in skip:
            continue
        try:
            run_one(task, cond, rep)
        except Exception as e:  # 하나가 실패해도 끝까지 간다
            print("RUNNER ERROR", task, cond, rep, repr(e), flush=True)


if __name__ == "__main__":
    main()
