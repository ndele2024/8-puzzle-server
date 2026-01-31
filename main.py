from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from puzzle.heuristic import ManhattanDistance, HammingDistance
from puzzle.solver import PuzzleSolver
from puzzle.solver_strategy import BfsStrategy, AstarStrategy
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
    #algorithm: str = "a_star"  # "bfs", "a_star", "ida_star"
    #heuristic: str = "manhattan"  # "manhattan", "hamming", "linear_conflict"

class SolveResponse(BaseModel):
    solutionBFS: Tuple[List[str], int, float]
    solutionAstart1: Tuple[List[str], int, float]
    solutionAstart2: Tuple[List[str], int, float]

@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(request: SolveRequest):
    try:
        initial_state = PuzzleState(board=request.initial_state, empty_position=request.empty_position)

        puzzle_solver_bfs = PuzzleSolver(BfsStrategy())
        puzzle_solver_aStart1 = PuzzleSolver(AstarStrategy(ManhattanDistance()))
        puzzle_solver_aStart2 = PuzzleSolver(AstarStrategy(HammingDistance()))

        #BFS solve
        start_time = time.time()
        final_state1, cost1 = puzzle_solver_bfs.solver.solve(initial_state)
        time_elapsed1 = time.time() - start_time

        # A* solve it with Manhattan distance
        start_time = time.time()
        final_state2, cost2 = puzzle_solver_aStart1.solver.solve(initial_state)
        time_elapsed2 = time.time() - start_time

        # A* solve it with Hamming distance
        start_time = time.time()
        final_state3, cost3 = puzzle_solver_aStart2.solver.solve(initial_state)
        time_elapsed3 = time.time() - start_time

        return {
            "solutionBFS": (puzzle_solver_bfs.reconstruct_path(final_state1), cost1, time_elapsed1),
            "solutionAstart1": (puzzle_solver_aStart1.reconstruct_path(final_state2), cost2, time_elapsed2),
            "solutionAstart2": (puzzle_solver_aStart2.reconstruct_path(final_state3), cost3, time_elapsed3)
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
