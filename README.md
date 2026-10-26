# 8-Puzzle AI Search Visualizer

Interactive Python/Streamlit 8-puzzle game. It includes **BFS**, **DFS**, **IDDFS**, **A\* Manhattan** and **A\* Euclidean**.

## Run locally (recommended)

1. Install Python 3.10+ and VS Code.
2. Open this project folder in a terminal.
3. Install dependencies: `pip install -r requirements.txt`
4. Launch: `streamlit run app.py`
5. The web app opens in your browser.

## Features

- Blue-themed puzzle visualization, based on the project design direction
- Input a state; shuffle to a guaranteed solvable state; reset
- BFS/DFS/IDDFS algorithm selector
- Step-by-step solution playback, previous/next, and short animations
- Path cost, expanded nodes, solution depth, and execution time
- Result download and explanatory text
- Unsolvable-state validation and solver-path validation

## Teammate integration instructions

Place any new algorithm in `algorithms.py` or import it from another file. It must accept a puzzle tuple and return `(moves, expanded, elapsed_seconds, search_depth)`, where `moves` is a list of blank directions (`'Up'`, `'Down'`, `'Left'`, `'Right'`). Return `None` for `moves` if no solution is found.

Add to `ALGORITHMS` in `algorithms.py`, for example:

```python
from astar import astar_manhattan, astar_euclidean

ALGORITHMS = {
    'BFS': bfs,
    'DFS': dfs,
    'IDDFS': iddfs,
    'A* Manhattan': astar_manhattan,
    'A* Euclidean': astar_euclidean,
}
```

No changes to the application selector or statistics panel should be needed.

## Notes for report

- Goal is `(0,1,2,3,4,5,6,7,8)`.
- Each blank move costs 1.
- Move order is Up, Down, Left, Right.
- BFS marks states visited on discovery and tests the goal when generating successors.
- DFS marks states visited on popping and tests goal when popping.
- IDDFS counts expanded states across **all iterations**; revisits in subsequent passes count again.
- Expanded nodes do not count goal tests, when no successors were generated.
- DFS can return a very long non-optimal solution, and IDDFS can be slow on hard boards.
- `shuffle_from_goal()` creates solvable states, but its step count is not necessarily the optimal solution depth.
- `Search depth` in the app means the depth of the returned goal, not maximum frontier depth.

## Test quickly

Run `python test_algorithms.py`.
