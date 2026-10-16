"""fixture 점검: 손대지 않은 상태에서는 세 테스트가 모두 실패하고,
참고 해답(UTF-8 명시)을 넣으면 통과하는지, 인코딩을 빼먹은 해답은 실패하는지 본다."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import FIXTURE, RUNS, TASKS, fresh_copy, grade, sha

prompts = json.loads((FIXTURE / "prompts.json").read_text(encoding="utf-8"))

GOOD = {
    "parse-log": ("parse.py", '''import re
rows = []
with open("sample.log", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"(\\S+ \\S+) ERROR\\s+\\[(.+?)\\] (.*)", line.rstrip("\\n"))
        if m:
            rows.append(m.groups())
with open("errors.md", "w", encoding="utf-8") as f:
    f.write("| 시각 | 모듈 | 메시지 |\\n|---|---|---|\\n")
    for r in rows:
        f.write("| " + " | ".join(r) + " |\\n")
'''),
    "csv-summary": ("summarize.py", '''import csv, json
t = {}
with open("sales.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        t[r["지역"]] = t.get(r["지역"], 0) + int(r["금액"])
with open("summary.json", "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False)
'''),
    "fix-failing": ("report.py", '''def load_names(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_report(names, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, name in enumerate(names, 1):
            f.write(f"{i}. {name} — 확인 완료\\n")
'''),
}

ok = True
manifest = {}
for task in TASKS:
    test = prompts[task]["test"]
    for f in sorted((FIXTURE / task).iterdir()):
        manifest[f"{task}/{f.name}"] = sha(f)
    # 1) 원본 그대로: 실패해야 한다
    d = RUNS / "_check" / f"{task}__raw"
    fresh_copy(task, d)
    g = grade(d, test)
    print(task, "raw passed =", g["passed"])
    ok &= not g["passed"]
    # 2) 인코딩 없는 해답: 실패해야 한다
    d = RUNS / "_check" / f"{task}__noenc"
    fresh_copy(task, d)
    name, code = GOOD[task]
    (d / name).write_text(code.replace(', encoding="utf-8"', ""), encoding="utf-8")
    g = grade(d, test)
    print(task, "no-encoding passed =", g["passed"])
    ok &= not g["passed"]
    # 3) 참고 해답: 통과해야 한다
    d = RUNS / "_check" / f"{task}__good"
    fresh_copy(task, d)
    (d / name).write_text(code, encoding="utf-8")
    g = grade(d, test)
    print(task, "good passed =", g["passed"], "" if g["passed"] else g["output_tail"])
    ok &= g["passed"]

(FIXTURE / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
print("FIXTURE OK" if ok else "FIXTURE PROBLEM")
