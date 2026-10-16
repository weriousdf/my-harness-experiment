"""parse-log 확인 테스트. 인코딩 설정이 없는 기본 Windows 환경에서 parse.py를 돌린다."""
import os
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED = [
    ("2026-10-16 09:01:12", "결제", "카드 승인 실패 — 한도 초과"),
    ("2026-10-16 09:03:44", "주문", "재고 부족 — 상품번호 A-102"),
    ("2026-10-16 09:05:59", "번역", "파일 형식 오류 — 한글(hwp) 변환 실패"),
    ("2026-10-16 09:08:47", "배송", "송장 번호 중복 — 재발급 필요"),
]


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}


class TestParse(unittest.TestCase):
    def test_errors_table(self):
        out = HERE / "errors.md"
        if out.exists():
            out.unlink()
        r = subprocess.run([sys.executable, "parse.py"], cwd=HERE, env=clean_env(), capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))
        text = out.read_text(encoding="utf-8")
        rows = []
        for line in text.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3 and not set(cells[0]) <= set("-: "):
                rows.append(tuple(cells))
        self.assertEqual(rows[1:], EXPECTED)  # 첫 행은 머리글


if __name__ == "__main__":
    unittest.main()
