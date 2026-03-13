from typing import List, Tuple
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from puzzle.heuristic import HammingDistance, ManhattanDistance
from puzzle.solver import PuzzleSolver
from puzzle.solver_strategy import (
    AstarStrategy,
    BfsStrategy,
    DfsStrategy,
    IdaStarStrategy,
)
from puzzle.state import PuzzleState


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolveRequest(BaseModel):
    initial_state: List[List[int]]
    empty_position: Tuple[int, int]
    algorithm: str
    heuristic: str


class SolveResponse(BaseModel):
    solutionBFS: Tuple[List[str], int, float]
    solutionDFS: Tuple[List[str], int, float]
    solutionAStar: Tuple[List[str], int, float]
    solutionIdastart: Tuple[List[str], int, float]


class SolveResponseBfs(BaseModel):
    solutionBFS: Tuple[List[str], int, float]


class SolveResponseDfs(BaseModel):
    solutionDFS: Tuple[List[str], int, float]


class SolveResponseAStar(BaseModel):
    solutionAStar: Tuple[List[str], int, float]


class SolveResponseIdaStar(BaseModel):
    solutionIdastart: Tuple[List[str], int, float]


def get_heuristic(heuristic_name: str):
    # On normalise la valeur recue pour eviter les surprises dues a la casse.
    if heuristic_name.lower() == "manhattan":
        return ManhattanDistance()
    return HammingDistance()


def build_initial_state(request: SolveRequest) -> PuzzleState:
    # Toute l'API reutilise la meme construction et la meme validation
    # pour garantir des comportements coherents entre les endpoints.
    initial_state = PuzzleState(
        board=request.initial_state,
        empty_position=request.empty_position,
    )
    initial_state.validate()
    return initial_state


def run_solver(puzzle_solver: PuzzleSolver, initial_state: PuzzleState) -> Tuple[List[str], int, float]:
    # Ce helper centralise l'execution d'un solveur: mesure du temps,
    # reconstruction du chemin et gestion explicite des cas sans solution.
    start_time = time.time()
    final_state, cost = puzzle_solver.solver.solve(initial_state)
    time_elapsed = time.time() - start_time

    if final_state is None:
        raise ValueError("Ce puzzle n'a pas de solution.")

    return puzzle_solver.reconstruct_path(final_state), cost, time_elapsed


@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = build_initial_state(request)

        puzzle_solver_bfs = PuzzleSolver(BfsStrategy())
        puzzle_solver_dfs = PuzzleSolver(DfsStrategy())
        heuristic = get_heuristic(request.heuristic)
        puzzle_solver_astart = PuzzleSolver(AstarStrategy(heuristic))
        puzzle_solver_ida_star = PuzzleSolver(IdaStarStrategy(heuristic))

        bfs_solve = run_solver(puzzle_solver_bfs, initial_state)
        dfs_solve = run_solver(puzzle_solver_dfs, initial_state)
        astart_solve = run_solver(puzzle_solver_astart, initial_state)
        idastart_solve = run_solver(puzzle_solver_ida_star, initial_state)

        return {
            "solutionBFS": bfs_solve,
            "solutionDFS": dfs_solve,
            "solutionAStar": astart_solve,
            "solutionIdastart": idastart_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/solveBFS", response_model=SolveResponseBfs)
async def solve_puzzle_bfs(request: SolveRequest):
    try:
        initial_state = build_initial_state(request)
        puzzle_solver_bfs = PuzzleSolver(BfsStrategy())

        return {
            "solutionBFS": run_solver(puzzle_solver_bfs, initial_state),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/solveDFS", response_model=SolveResponseDfs)
async def solve_puzzle_dfs(request: SolveRequest):
    try:
        initial_state = build_initial_state(request)
        puzzle_solver_dfs = PuzzleSolver(DfsStrategy())

        return {
            "solutionDFS": run_solver(puzzle_solver_dfs, initial_state),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/solveAStar", response_model=SolveResponseAStar)
async def solve_puzzle_astar(request: SolveRequest):
    try:
        initial_state = build_initial_state(request)
        heuristic = get_heuristic(request.heuristic)
        puzzle_solver_astart = PuzzleSolver(AstarStrategy(heuristic))

        return {
            "solutionAStar": run_solver(puzzle_solver_astart, initial_state),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/solveIdaStar", response_model=SolveResponseIdaStar)
async def solve_puzzle_idastar(request: SolveRequest):
    try:
        initial_state = build_initial_state(request)
        heuristic = get_heuristic(request.heuristic)
        puzzle_solver_idastart = PuzzleSolver(IdaStarStrategy(heuristic))

        return {
            "solutionIdastart": run_solver(puzzle_solver_idastart, initial_state),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/random_puzzle")
async def random_puzzle():
    puzzle = PuzzleState.generate_random_state()
    return {"initial_state": puzzle.board, "empty_position": puzzle.empty_position}
