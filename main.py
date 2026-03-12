from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from puzzle.heuristic import ManhattanDistance, HammingDistance
from puzzle.solver import PuzzleSolver
from puzzle.solver_strategy import BfsStrategy, DfsStrategy, AstarStrategy, IdaStarStrategy
from puzzle.state import PuzzleState
from typing import List, Tuple
import time


app = FastAPI()

# Configuration CORS
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
    algorithm: str  # "bfs", "a_star", "ida_star"
    heuristic: str  # "manhattan", "hamming", "linear_conflicts"

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


@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)

        puzzle_solver_bfs = PuzzleSolver(BfsStrategy())
        puzzle_solver_dfs = PuzzleSolver(DfsStrategy())
        heuristic = ManhattanDistance() if request.heuristic == "manhattan" else HammingDistance()
        puzzle_solver_astart = PuzzleSolver(AstarStrategy(heuristic))
        puzzle_solver_ida_star = PuzzleSolver(IdaStarStrategy(heuristic))
        #bfs_solve, aStart_solve = None, None

        # BFS solve
        start_time = time.time()
        final_state, cost = puzzle_solver_bfs.solver.solve(initial_state)
        time_elapsed = time.time() - start_time
        bfs_solve = (puzzle_solver_bfs.reconstruct_path(final_state), cost, time_elapsed)

        # DFS solve
        start_time = time.time()
        final_state, cost = puzzle_solver_dfs.solver.solve(initial_state)
        time_elapsed = time.time() - start_time
        dfs_solve = (puzzle_solver_dfs.reconstruct_path(final_state), cost, time_elapsed)

        # A* solve
        start_time = time.time()
        final_state, cost = puzzle_solver_astart.solver.solve(initial_state)
        time_elapsed = time.time() - start_time
        astart_solve = (puzzle_solver_astart.reconstruct_path(final_state), cost, time_elapsed)

        #ida* solve
        start_time = time.time()
        final_state, cost = puzzle_solver_ida_star.solver.solve(initial_state)
        time_elapsed = time.time() - start_time
        idastart_solve = (puzzle_solver_astart.reconstruct_path(final_state), cost, time_elapsed)

        return {
            "solutionBFS": bfs_solve,
            "solutionDFS": dfs_solve,
            "solutionAStar": astart_solve,
            "solutionIdastart": idastart_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solveBFS", response_model=SolveResponseBfs)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)
        puzzle_solver_bfs = PuzzleSolver(BfsStrategy())

        #BFS solve
        start_time = time.time()
        final_state1, cost1 = puzzle_solver_bfs.solver.solve(initial_state)
        time_elapsed1 = time.time() - start_time
        bfs_solve = (puzzle_solver_bfs.reconstruct_path(final_state1), cost1, time_elapsed1)

        return {
            "solutionBFS": bfs_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solveDFS", response_model=SolveResponseDfs)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)
        puzzle_solver_dfs = PuzzleSolver(DfsStrategy())

        #BFS solve
        start_time = time.time()
        final_state1, cost1 = puzzle_solver_dfs.solver.solve(initial_state)
        time_elapsed1 = time.time() - start_time
        dfs_solve = (puzzle_solver_dfs.reconstruct_path(final_state1), cost1, time_elapsed1)

        return {
            "solutionDFS": dfs_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solveAStar", response_model=SolveResponseAStar)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)
        heuristic = ManhattanDistance() if request.heuristic == "manhattan" else HammingDistance()
        puzzle_solver_astart = PuzzleSolver(AstarStrategy(heuristic))

        # A* solve it with heuristic
        start_time = time.time()
        final_state2, cost2 = puzzle_solver_astart.solver.solve(initial_state)
        time_elapsed2 = time.time() - start_time
        astart_solve = (puzzle_solver_astart.reconstruct_path(final_state2), cost2, time_elapsed2)

        return {
            "solutionAStar": astart_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solveIdaStar", response_model=SolveResponseIdaStar)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)
        heuristic = ManhattanDistance() if request.heuristic == "manhattan" else HammingDistance()
        puzzle_solver_idastart = PuzzleSolver(IdaStarStrategy(heuristic))

        # IDA* solve
        start_time = time.time()
        final_state2, cost2 = puzzle_solver_idastart.solver.solve(initial_state)
        time_elapsed2 = time.time() - start_time
        idastart_solve = (puzzle_solver_idastart.reconstruct_path(final_state2), cost2, time_elapsed2)

        return {
            "solutionIdastart": idastart_solve,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/random_puzzle")
async def random_puzzle():
    puzzle = PuzzleState.generate_random_state()
    return {"initial_state": puzzle.board, "empty_position": puzzle.empty_position}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
