from core.utils import retry


def test_retry() -> None:
    tries = {"n": 0}

    def fn() -> str:
        tries["n"] += 1
        if tries["n"] < 3:
            raise RuntimeError("no")
        return "ok"

    assert retry(fn, attempts=3) == "ok"
