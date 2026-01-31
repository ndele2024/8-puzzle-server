from typing import List
import heapq

from puzzle.solver_strategy import IsolverStrategy
from puzzle.state import PuzzleState


class PuzzleSolver:
  solver : IsolverStrategy

  def __init__(self, solver : IsolverStrategy):
    self.solver = solver

  def reconstruct_path(self, state: PuzzleState) -> List[str]:
    path = []
    current = state
    while current.parent is not None:
        path.append(current.move)
        current = current.parent
    #Inverser pour avoir l'ordre correct
    return path[::-1]
