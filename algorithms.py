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

import math

# GOAL_POS[tile] = (row, col) of that tile in the goal state.
# Because GOAL = (0,1,...,8), tile t sits at index t, i.e. (t // 3, t % 3).
GOAL_POS = {tile: divmod(idx, 3) for idx, tile in enumerate(GOAL)}


def manhattan(state):
    """Sum over tiles 1..8 of |row - goal_row| + |col - goal_col|."""
    total = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(idx, 3)
        gr, gc = GOAL_POS[tile]
        total += abs(r - gr) + abs(c - gc)
    return total


def euclidean(state):
    """Sum over tiles 1..8 of sqrt((row - goal_row)^2 + (col - goal_col)^2)."""
    total = 0.0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(idx, 3)
        gr, gc = GOAL_POS[tile]
        total += math.sqrt((r - gr) ** 2 + (c - gc) ** 2)
    return total


class Heap:
    """Min-heap with the lecture's operations: insert, deleteMin, decreaseKey,
    isEmpty, and membership ('state in frontier')."""

    def __init__(self):
        self.heap = []        # entries: [key, order, state]
        self.pos = {}         # state -> index in self.heap
        self.order = 0        # insertion counter: breaks ties first-in-first-out

    def isEmpty(self):
        return len(self.heap) == 0

    def __contains__(self, state):          # enables: state in frontier
        return state in self.pos

    def insert(self, state, key):
        self.order += 1
        self.heap.append([key, self.order, state])
        self.pos[state] = len(self.heap) - 1
        self._sift_up(len(self.heap) - 1)

    def deleteMin(self):
        root = self.heap[0]
        last = self.heap.pop()
        del self.pos[root[2]]
        if self.heap:                        # move last entry to the root and push it down
            self.heap[0] = last
            self.pos[last[2]] = 0
            self._sift_down(0)
        return root[2]

    def decreaseKey(self, state, new_key):
        """Lower the key of a state already in the heap. Returns True if the key
        actually decreased (a cheaper path was found), False otherwise."""
        i = self.pos[state]
        if new_key < self.heap[i][0]:
            self.heap[i][0] = new_key
            self._sift_up(i)                 # a smaller key can only move up
            return True
        return False

    # ---- internal helpers ----
    def _less(self, i, j):                   # compare by key, then by insertion order
        return self.heap[i][:2] < self.heap[j][:2]

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos[self.heap[i][2]] = i
        self.pos[self.heap[j][2]] = j

    def _sift_up(self, i):
        while i > 0:
            p = (i - 1) // 2
            if self._less(i, p):
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        n = len(self.heap)
        while True:
            smallest, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and self._less(l, smallest):
                smallest = l
            if r < n and self._less(r, smallest):
                smallest = r
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest


def astar(start, heuristic=manhattan):
    """A* exactly as in the lecture's A-STAR-SEARCH pseudocode, with f(n) = g(n) + h(n)."""
    t0 = time.perf_counter()
    g = {start: 0}                           # g(n): cost from start to n
    parent = {start: None}                   # for reconstruct()
    expanded = 0

    frontier = Heap()                        # frontier = Heap.new(initialState)
    frontier.insert(start, g[start] + heuristic(start))
    explored = set()                         # explored = Set.new()

    while not frontier.isEmpty():            # while not frontier.isEmpty():
        state = frontier.deleteMin()         #     state = frontier.deleteMin()
        explored.add(state)                  #     explored.add(state)

        if state == GOAL:                    #     if goalTest(state):
            moves = reconstruct(parent, state)   #     return SUCCESS(state)
            return moves, expanded, time.perf_counter() - t0, g[state]

        expanded += 1
        for move, neighbor in neighbors(state):          # for neighbor in state.neighbors():
            new_g = g[state] + 1                         # every move costs 1
            f = new_g + heuristic(neighbor)
            if neighbor not in frontier and neighbor not in explored:   # not in frontier ∪ explored
                g[neighbor] = new_g
                parent[neighbor] = (state, move)
                frontier.insert(neighbor, f)             #     frontier.insert(neighbor)
            elif neighbor in frontier:                   # else if neighbor in frontier:
                if frontier.decreaseKey(neighbor, f):    #     frontier.decreaseKey(neighbor)
                    g[neighbor] = new_g                  # cheaper path found: remember it
                    parent[neighbor] = (state, move)

    return None, expanded, time.perf_counter() - t0, 0   # return FAILURE


def astar_manhattan(start):
    return astar(start, manhattan)


def astar_euclidean(start):
    return astar(start, euclidean)

ALGORITHMS = {
    'BFS': bfs,
    'DFS': dfs,
    'IDDFS': iddfs,
    'A* Manhattan': astar_manhattan,
    'A* Euclidean': astar_euclidean,
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
