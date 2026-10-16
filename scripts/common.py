"""실험 공통: 경로, 깨끗한 환경, 채점."""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixture"
RUNS = pathlib.Path(r"D:\aiffel_work\261016\runs")  # 저장소 밖 작업 폴더
TASKS = ["parse-log", "csv-summary", "fix-failing"]


def clean_env():
    """전역 설정의 PYTHONUTF8·PYTHONIOENCODING을 뺀 기본 Windows 환경."""
    return {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:16]


def fresh_copy(task, dest, claude_md=None):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(FIXTURE / task, dest)
    if claude_md:
        shutil.copy(FIXTURE / "conditions" / claude_md, dest / "CLAUDE.md")


def grade(workdir, test):
    """기본 python(UTF-8 모드 꺼짐)으로 테스트를 돌린다. 테스트 파일이 바뀌었으면 실패."""
    task = workdir.name.split("__")[0] if "__" in workdir.name else None
    tampered = False
    if task:
        for f in (FIXTURE / task).iterdir():
            if f.name.startswith("test_") or f.suffix in (".log", ".csv", ".txt"):
                if not (workdir / f.name).exists() or sha(workdir / f.name) != sha(f):
                    tampered = True
    r = subprocess.run([sys.executable, test], cwd=workdir, env=clean_env(), capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return {"passed": r.returncode == 0 and not tampered, "returncode": r.returncode,
            "tampered": tampered, "output_tail": out[-1500:]}
