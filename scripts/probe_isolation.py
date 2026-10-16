"""격리 확인용: 전역 CLAUDE.md·전역 env가 하위 claude에 들어가는지 본다."""
import json, os, subprocess, sys, pathlib

mode = sys.argv[1] if len(sys.argv) > 1 else "exclude"
d = pathlib.Path(r"D:\aiffel_work\261016\runs\probe")
d.mkdir(parents=True, exist_ok=True)
(d / "CLAUDE.md").write_text("CANARY-PROJECT-7731\n", encoding="utf-8")
(d / "probe.py").write_text(
    "import sys,os,locale;print(sys.flags.utf8_mode, os.environ.get('PYTHONUTF8'), "
    "os.environ.get('PYTHONIOENCODING'), locale.getpreferredencoding())\n", encoding="utf-8")
settings = d / "probe_settings.json"
settings.write_text(json.dumps({"claudeMdExcludes": [
    "C:/Users/bk_ma/.claude/CLAUDE.md", "C:\\Users\\bk_ma\\.claude\\CLAUDE.md"], "autoMemoryEnabled": False}), encoding="utf-8")

env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}
env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
p = ("Answer in English, briefly. (1) Do your instructions mention a person named Bogyeom? yes/no. "
     "(2) Quote any CANARY string in your instructions. (2b) Do your instructions or memory say anything about UTF-8, encoding or Korean? Quote it or say none. (2c) List every instruction/memory source file path you were given. (3) Run: python probe.py  and report its output verbatim.")
cmd = ["claude", "-p", p, "--model", "claude-sonnet-5-5", "--setting-sources", "project,local",
       "--strict-mcp-config", "--allowedTools", "Bash", "--output-format", "json", "--no-session-persistence"]
if mode == "exclude":
    cmd += ["--settings", str(settings)]
r = subprocess.run(cmd, cwd=d, env=env, capture_output=True, encoding="utf-8")
print("stderr:", r.stderr[:300])
o = json.loads(r.stdout)
print(o["result"])
u = o["usage"]
print("cost", o["total_cost_usd"], "cache_create", u["cache_creation_input_tokens"], "cache_read", u["cache_read_input_tokens"])
