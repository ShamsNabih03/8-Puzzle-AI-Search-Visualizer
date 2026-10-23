"""8-puzzle solver algorithms. Other team members can add new algorithms here.

All functions return (moves, expanded_nodes, elapsed_seconds, search_depth).
Moves refer to the direction the EMPTY tile (0) moves.
"""
import time
from collections import deque

GOAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)
MOVES = [('Up', -1, 0), ('Down', 1, 0), ('Left', 0, -1), ('Right', 0, 1)]


def neighbors(state):
    i = state.index(0)
    r, c = divmod(i, 3)
    result = []
    for name, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            j = nr * 3 + nc
            s = list(state)
            s[i], s[j] = s[j], s[i]
            result.append((name, tuple(s)))
    return result


def is_solvable(state):
    tiles = [t for t in state if t != 0]
    inv = sum(tiles[i] > tiles[j]
              for i in range(len(tiles))
              for j in range(i + 1, len(tiles)))
    return inv % 2 == 0


def reconstruct(parent, state):
    moves = []
    while parent[state] is not None:
        state, move = parent[state]
        moves.append(move)
    return moves[::-1]


def bfs(start):
    t0 = time.perf_counter()
    parent = {start: None}
    depth = {start: 0}
    frontier = deque([start])
    expanded = 0
    if start == GOAL:
        return [], 0, time.perf_counter() - t0, 0
    while frontier:
        s = frontier.popleft()
        expanded += 1
        for move, n in neighbors(s):
            if n not in parent:
                parent[n] = (s, move)
                depth[n] = depth[s] + 1
                if n == GOAL:
                    moves = reconstruct(parent, n)
                    return moves, expanded, time.perf_counter() - t0, depth[n]
                frontier.append(n)
    return None, expanded, time.perf_counter() - t0, 0


def dfs(start):
    t0 = time.perf_counter()
    parent = {}
    stack = [(start, None, None, 0)]
    expanded, max_depth = 0, 0
    while stack:
        s, p, m, d = stack.pop()
        if s in parent:
            continue
        parent[s] = None if p is None else (p, m)
        max_depth = max(max_depth, d)
        if s == GOAL:
            moves = reconstruct(parent, s)
            # Return solution depth consistently. The deepest processed node is
            # available in max_depth for a future separate diagnostic metric.
            return moves, expanded, time.perf_counter() - t0, len(moves)
        expanded += 1
        for move, n in reversed(neighbors(s)):
            if n not in parent:
                stack.append((n, s, move, d + 1))
    return None, expanded, time.perf_counter() - t0, 0


def iddfs(start, max_limit=40):
    t0 = time.perf_counter()
    expanded = 0

    def dls(state, limit, on_path):
        nonlocal expanded
        if state == GOAL:
            return []
        if limit == 0:
            return None
        expanded += 1
        for move, n in neighbors(state):
            if n not in on_path:
                on_path.add(n)
                result = dls(n, limit - 1, on_path)
                on_path.remove(n)
                if result is not None:
                    return [move] + result
        return None

    for limit in range(max_limit + 1):
        moves = dls(start, limit, {start})
        if moves is not None:
            return moves, expanded, time.perf_counter() - t0, limit
    return None, expanded, time.perf_counter() - t0, max_limit


# TEAM INTEGRATION POINT: import teammates' algorithms and add them here.
# e.g. from astar import astar_manhattan, astar_euclidean
ALGORITHMS = {
    'BFS': bfs,
    'DFS': dfs,
    'IDDFS': iddfs,
    # 'A* Manhattan': astar_manhattan,
    # 'A* Euclidean': astar_euclidean,
}


def build_states(initial, moves):
    """Return a state for every step, including the initial configuration."""
    states = [tuple(initial)]
    current = tuple(initial)
    for move in moves:
        options = dict(neighbors(current))
        if move not in options:
            raise ValueError(f'Invalid move {move} from {current}')
        current = options[move]
        states.append(current)
    if current != GOAL:
        raise ValueError('A solver returned a path that does not reach the goal')
    return states


def shuffle_from_goal(steps=8, seed=None):
    """Create guaranteed solvable puzzles with a controllable shuffle depth."""
    import random
    rng = random.Random(seed)
    state = GOAL
    previous = None
    for _ in range(steps):
        options = [(move, s) for move, s in neighbors(state) if s != previous]
        move, candidate = rng.choice(options)
        previous, state = state, candidate
    return state
