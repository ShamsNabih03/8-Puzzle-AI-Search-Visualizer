from algorithms import GOAL, bfs, dfs, iddfs, build_states, is_solvable, neighbors

start = (1, 2, 5, 3, 4, 0, 6, 7, 8)
for solver in (bfs, dfs, iddfs):
    moves, expanded, duration, depth = solver(start)
    assert moves is not None
    assert build_states(start, moves)[-1] == GOAL
    assert depth == len(moves)
    assert expanded >= 0
    print(f'{solver.__name__}: moves={len(moves)}, expanded={expanded}, seconds={duration:.6f}')
assert len(bfs(start)[0]) == 3
assert len(iddfs(start)[0]) == 3
assert not is_solvable((0, 2, 1, 3, 4, 5, 6, 7, 8))
assert len(neighbors(start)) == 3
print('All tests passed.')
