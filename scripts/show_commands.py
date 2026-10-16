"""trace에서 셸 명령과 그 결과 앞부분을 순서대로 보여 준다. 사용: show_commands.py <run_id>..."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import REPO

for run_id in sys.argv[1:]:
    print("=====", run_id)
    pending = {}
    for ln in (REPO / "traces" / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        content = ev.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for b in content:
            if b.get("type") == "tool_use":
                inp = b.get("input", {})
                desc = inp.get("command") or inp.get("file_path") or ""
                pending[b["id"]] = f"{b['name']}: {desc[:160]}"
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                c = b.get("content")
                t = c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
                print("-", pending.pop(b["tool_use_id"]))
                print("   ->", " ".join(t.split())[:220])
