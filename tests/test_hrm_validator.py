from core.sudoku import is_valid_sudoku, valid_81


def test_len() -> None:
    assert valid_81("0" * 81)
    assert not valid_81("0" * 80)


def test_valid() -> None:
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    assert is_valid_sudoku(grid)
