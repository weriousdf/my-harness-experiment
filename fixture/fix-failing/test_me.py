"""fix-failing 확인 테스트. 기본 Windows 환경(cp949)에서 실패 2건이 나온다."""
import pathlib
import tempfile
import unittest

import report

HERE = pathlib.Path(__file__).resolve().parent


class TestReport(unittest.TestCase):
    def test_load_names(self):
        self.assertEqual(report.load_names(HERE / "names.txt"),
                         ["김민수 — 서울", "이서연 — 부산", "박지훈 — 대구"])

    def test_save_report(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "out.txt"
            report.save_report(["김민수 — 서울"], p)
            self.assertEqual(p.read_text(encoding="utf-8"), "1. 김민수 — 서울 — 확인 완료\n")


if __name__ == "__main__":
    unittest.main()
