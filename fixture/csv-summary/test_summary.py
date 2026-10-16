"""csv-summary 확인 테스트. 인코딩 설정이 없는 기본 Windows 환경에서 summarize.py를 돌린다."""
import json
import os
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED = {"서울": 250000, "부산": 190000, "대구": 170000, "제주": 50000}


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}


class TestSummary(unittest.TestCase):
    def setUp(self):
        out = HERE / "summary.json"
        if out.exists():
            out.unlink()
        r = subprocess.run([sys.executable, "summarize.py"], cwd=HERE, env=clean_env(), capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))
        self.raw = (HERE / "summary.json").read_bytes().decode("utf-8")

    def test_totals(self):
        self.assertEqual(json.loads(self.raw), EXPECTED)

    def test_korean_not_escaped(self):
        self.assertIn("서울", self.raw)


if __name__ == "__main__":
    unittest.main()
