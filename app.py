"""Interactive 8-puzzle game built with Streamlit."""
import html
import re
import time
from pathlib import Path

import streamlit as st

from algorithms import GOAL, ALGORITHMS, build_states, is_solvable, neighbors, shuffle_from_goal

st.set_page_config(page_title='8 Puzzle Solver', page_icon='🧩', layout='centered')

with Path(__file__).with_name('style.css').open(encoding='utf-8') as file:
    st.markdown(f'<style>{file.read()}</style>', unsafe_allow_html=True)

DEFAULT = (1, 2, 5, 3, 4, 0, 6, 7, 8)


def reset_solution():
    st.session_state.solution = None
    st.session_state.step = 0
    st.session_state.result = None


if 'board' not in st.session_state:
    st.session_state.board = DEFAULT
    st.session_state.entry = ', '.join(map(str, DEFAULT))
    reset_solution()


def parse_board(raw):
    parts = [p for p in re.split(r'[\s,;]+', raw.strip()) if p]
    if len(parts) != 9 or not all(p in [str(i) for i in range(9)] for p in parts):
        raise ValueError('Enter exactly nine numbers from 0 to 8, separated by commas or spaces.')
    board = tuple(map(int, parts))
    if set(board) != set(range(9)):
        raise ValueError('Each number from 0 to 8 must appear exactly once.')
    if not is_solvable(board):
        raise ValueError('This board is unsolvable. Try Shuffle for a guaranteed solvable board.')
    return board


def puzzle_html(board, small=False):
    cells = ''.join(f'<div class="tile {"blank" if n == 0 else ""}">{n if n else ""}</div>' for n in board)
    return f'<div class="puzzle {"mini" if small else ""}">{cells}</div>'


st.markdown('<div class="hero-kicker">AI SEARCH VISUALIZER</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">8 Puzzle Solver</h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Explore the puzzle with Breadth-First, Depth-First and Iterative Deepening Search</div>', unsafe_allow_html=True)

def set_state_action():
    try:
        st.session_state.board = parse_board(st.session_state.entry)
        st.session_state.input_error = None
        reset_solution()
    except ValueError as ex:
        st.session_state.input_error = str(ex)


def shuffle_action():
    st.session_state.board = shuffle_from_goal(steps=8)
    st.session_state.entry = ', '.join(map(str, st.session_state.board))
    st.session_state.input_error = None
    reset_solution()


def reset_action():
    st.session_state.board = DEFAULT
    st.session_state.entry = ', '.join(map(str, DEFAULT))
    st.session_state.input_error = None
    reset_solution()


st.markdown('<div class="section-label">SET UP YOUR PUZZLE</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.text_input('Initial State · use 0 for the blank', key='entry', help='Example: 1, 2, 5, 3, 4, 0, 6, 7, 8')
    a, b, c = st.columns(3)
    a.button('Set State', use_container_width=True, on_click=set_state_action)
    b.button('↝ Shuffle', use_container_width=True, on_click=shuffle_action)
    c.button('↺ Reset', use_container_width=True, on_click=reset_action)
    if st.session_state.get('input_error'):
        st.error(st.session_state.input_error)

st.markdown('<div class="section-label">PUZZLE BOARD</div>', unsafe_allow_html=True)
solution = st.session_state.solution
index = st.session_state.step
board = solution[index] if solution else st.session_state.board
st.markdown('<div class="board-shell">' + puzzle_html(board) + '</div>', unsafe_allow_html=True)

if solution is not None:
    total = len(solution) - 1
    st.markdown(f'<p class="step-label">Step {index} of {total} · {"GOAL REACHED ✓" if index == total else "Solution playback"}</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="step-label">Move the tiles yourself or choose an algorithm to solve.</p>', unsafe_allow_html=True)

prev, nxt, play = st.columns(3)
if prev.button('◀ Previous', use_container_width=True, disabled=solution is None or index <= 0):
    st.session_state.step -= 1
    st.rerun()
if nxt.button('Next ▶', use_container_width=True, disabled=solution is None or index >= len(solution)-1):
    st.session_state.step += 1
    st.rerun()
if play.button('▶ Play all', use_container_width=True, disabled=solution is None or index >= len(solution)-1):
    # A modest animation through native Streamlit redraws. For very long DFS
    # paths we intentionally show only manual controls to avoid UI lock-ups.
    remaining = len(solution) - 1 - index
    if remaining > 120:
        st.warning('This DFS path is very long. Use Next/Previous instead, or choose BFS for a short playback.')
    else:
        board_holder = st.empty()
        status_holder = st.empty()
        for i in range(index+1, len(solution)):
            with board_holder.container():
                st.markdown('<div class="board-shell">' + puzzle_html(solution[i]) + '</div>', unsafe_allow_html=True)
            status_holder.caption(f'Animation · Step {i} / {len(solution)-1}')
            time.sleep(0.23)
        st.session_state.step = len(solution)-1
        st.rerun()

st.markdown('<div class="section-label">SEARCH CONTROLS</div>', unsafe_allow_html=True)
with st.container(border=True):
    selected = st.selectbox('Search algorithm', list(ALGORITHMS), help='A* methods can be added here by your teammates later.')
    if selected == 'IDDFS':
        st.caption('IDDFS repeats depth-limited DFS. Hard puzzles can take a long time.')
        max_limit = st.slider('Maximum IDDFS depth', 3, 40, 31)
    else:
        max_limit = 40
    if selected == 'DFS':
        st.caption('DFS might return a very long (non-optimal) solution. The animation has a safety limit.')
    if st.button('✦ Solve Puzzle', type='primary', use_container_width=True):
        with st.spinner(f'Running {selected}...'):
            if selected == 'IDDFS':
                moves, expanded, elapsed, depth = ALGORITHMS[selected](st.session_state.board, max_limit=max_limit)
            else:
                moves, expanded, elapsed, depth = ALGORITHMS[selected](st.session_state.board)
        if moves is None:
            reset_solution()
            st.warning('No solution found within the search limit.')
        else:
            try:
                states = build_states(st.session_state.board, moves)
            except ValueError as ex:
                st.error(f'Solver validation failed: {ex}')
            else:
                st.session_state.solution = states
                st.session_state.result = {'algorithm': selected, 'moves': moves, 'expanded': expanded,
                                           'time': elapsed, 'depth': depth}
                st.session_state.step = 0
                st.rerun()

if st.session_state.result is not None:
    result = st.session_state.result
    st.markdown('<div class="section-label">SEARCH STATISTICS</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric('Path cost', len(result['moves']))
    cols[1].metric('Nodes expanded', f"{result['expanded']:,}")
    cols[2].metric('Search depth', result['depth'])
    cols[3].metric('Runtime', f"{result['time']:.4f}s")
    with st.expander('Show complete solution path'):
        st.write(' → '.join(result['moves']) if result['moves'] else 'Already solved.')
        st.caption('The playback above shows every resulting board state.')
    st.download_button('Download results (TXT)',
                       data=f"Algorithm: {result['algorithm']}\nInitial: {st.session_state.board}\nGoal: {GOAL}\nPath cost: {len(result['moves'])}\nNodes expanded: {result['expanded']}\nSearch depth: {result['depth']}\nRuntime: {result['time']:.6f}s\nPath: {result['moves']}\n",
                       file_name='puzzle_search_results.txt', mime='text/plain')

with st.expander('Learn about the algorithms'):
    st.markdown('**BFS:** FIFO queue. Finds the minimum-move solution for unit-cost puzzles.\n\n'
                '**DFS:** LIFO stack. Explores one route deeply; does not guarantee the shortest solution.\n\n'
                '**IDDFS:** Repeats depth-limited DFS. Finds minimum moves with a sufficient depth limit; revisits states across iterations.\n\n'
                '**Movement order:** Up, Down, Left, Right (directions of the blank tile).')

st.markdown('<div class="footer-note">Alexandria University · Artificial Intelligence · Assignment 1</div>', unsafe_allow_html=True)
