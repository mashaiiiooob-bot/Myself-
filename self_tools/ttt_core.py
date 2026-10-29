"""Tic-tac-toe core: exact solver (minimax over the full 3x3 game tree) and move grading.
Positions are 9-character strings of 'X', 'O' and '.' (cells 0-8, row-major)."""
from functools import lru_cache

LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


def other(p):
    return "O" if p == "X" else "X"


def winner(b):
    for a, c, d in LINES:
        if b[a] != "." and b[a] == b[c] == b[d]:
            return b[a]
    return None


def is_terminal(b):
    return winner(b) is not None or "." not in b


def to_move(b, first="X"):
    """Whose turn it is, given who moved first. None if the counts are impossible."""
    x, o = b.count("X"), b.count("O")
    second = other(first)
    cf, cs = (x, o) if first == "X" else (o, x)
    if cf == cs:
        return first
    if cf == cs + 1:
        return second
    return None


def legal(b):
    return [i for i, c in enumerate(b) if c == "."]


def place(b, cell, p):
    return b[:cell] + p + b[cell + 1:]


@lru_cache(maxsize=None)
def solve(b, p):
    """Best achievable result for player p to move: +1 win, 0 draw, -1 loss."""
    w = winner(b)
    if w:
        return 1 if w == p else -1
    if "." not in b:
        return 0
    return max(move_value(b, i, p) for i in legal(b))


def move_value(b, cell, p):
    """Result for p after playing `cell` (both sides then play perfectly)."""
    nb = place(b, cell, p)
    w = winner(nb)
    if w:
        return 1
    if "." not in nb:
        return 0
    return -solve(nb, other(p))


def move_values(b, p):
    return {i: move_value(b, i, p) for i in legal(b)}


def optimal_cells(b, p):
    v = move_values(b, p)
    best = max(v.values())
    return [i for i, x in v.items() if x == best]


def grade(b, cell, p):
    """'optimal' | 'suboptimal' (gives away a win or a draw) | 'blunder' (turns a non-loss into a forced loss)."""
    v = move_values(b, p)
    if cell not in v:
        return "illegal"
    best = max(v.values())
    if v[cell] == best:
        return "optimal"
    return "blunder" if v[cell] == -1 and best > -1 else "suboptimal"


def optimal_share(b, p):
    """Probability that a uniformly random legal move is optimal (baseline for 'is it random?')."""
    opt, n = len(optimal_cells(b, p)), len(legal(b))
    return opt / n if n else 1.0


def suggest(b, p, model=None, model_key=""):
    """A move for p that never loses (and wins whenever a forced win exists).
    With a learned opponent model (position -> {reply_cell: count}) it breaks ties between equally safe moves by
    the best expected result against that opponent's usual replies; without one it prefers centre, then corners."""
    vals = move_values(b, p)
    if not vals:
        return None
    best = max(vals.values())
    cands = [i for i, v in vals.items() if v == best]          # never give up a forced win / a draw
    pref = lambda i: (i != 4, i not in (0, 2, 6, 8), i)
    if not model or len(cands) == 1:
        return sorted(cands, key=pref)[0]
    score = {1: 1.0, 0: 0.5, -1: -1.0}

    def ev(cell):
        nb = place(b, cell, p)
        if winner(nb):
            return 2.0
        if "." not in nb:
            return 0.5
        replies = model.get(model_key + nb) or {}
        tot = sum(replies.values())
        if not tot:
            return score[vals[cell]]
        s = 0.0
        for r, c in replies.items():
            nb2 = place(nb, int(r), other(p))
            s += c * (-1.0 if winner(nb2) else 0.5 if "." not in nb2 else score[solve(nb2, p)])
        return s / tot
    return max(cands, key=lambda i: (ev(i), -pref(i)[0], -pref(i)[1], -i))
