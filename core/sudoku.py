def valid_81(grid: str) -> bool:
    return len(grid) == 81 and all(ch.isdigit() for ch in grid)


def _rc(i: int) -> tuple[int, int]:
    return i // 9, i % 9


def is_valid_sudoku(grid: str) -> bool:
    if not valid_81(grid):
        return False
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i, ch in enumerate(grid):
        if ch in ("0", ".", " ", "\n"):
            continue
        r, c = _rc(i)
        b = (r // 3) * 3 + (c // 3)
        if ch in rows[r] or ch in cols[c] or ch in boxes[b]:
            return False
        rows[r].add(ch)
        cols[c].add(ch)
        boxes[b].add(ch)
    return True


def pretty(grid: str) -> str:
    rows = [grid[i : i + 9] for i in range(0, 81, 9)]
    return "\n".join(
        " ".join(ch if ch != "0" else "." for ch in r) for r in rows
    )
