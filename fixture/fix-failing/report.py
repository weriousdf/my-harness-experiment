"""명단을 읽어 확인 보고서를 쓰는 모듈."""


def load_names(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def save_report(names, path):
    with open(path, "w") as f:
        for i, name in enumerate(names, 1):
            f.write(f"{i}. {name} — 확인 완료\n")
