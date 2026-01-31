import heapq
from typing import Tuple, Any
from abc import abstractmethod, ABC

from puzzle import heuristic
from puzzle.heuristic import IHeuristic
from puzzle.state import PuzzleState


#Interface strategy for all diferents solvers methods
class IsolverStrategy(ABC):
  @abstractmethod
  def solve(self, initial_state: PuzzleState) -> Tuple[PuzzleState, int]:
    pass

#concrete strategy
class BfsStrategy(IsolverStrategy):
  def solve(self, initial_state: PuzzleState) -> tuple[PuzzleState, int] | tuple[None, int]:
    """Breadth-First Search - Garantit la solution optimale mais lent"""
    queue = [initial_state]
    visited = set()
    visited.add(initial_state)

    while queue:
      current = queue.pop(0)

      if current.is_goal():
        return current, current.cost

      for neighbor in current.get_neighbors():
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append(neighbor)

    return None, 0  # Pas de solution


class DfsStrategy(IsolverStrategy):
  def solve(self, initial_state: PuzzleState) -> Tuple[PuzzleState, int]:
    pass


class AstarStrategy(IsolverStrategy):
  heuristic : IHeuristic

  def __init__(self, heurist : IHeuristic):
    self.heuristic = heurist

  def solve(self, initial_state: PuzzleState) -> tuple[Any, Any] | tuple[None, int]:
    open_set = []
    heapq.heappush(open_set, (self.heuristic.calculate(initial_state), 0, initial_state))
    closed_set = set()

    while open_set:
      _, cost, current = heapq.heappop(open_set)

      if current.is_goal():
        return current, current.cost

      if current in closed_set:
        continue
      closed_set.add(current)

      for neighbor in current.get_neighbors():
        new_cost = cost + 1
        priority = new_cost + self.heuristic.calculate(neighbor)
        heapq.heappush(open_set, (priority, new_cost, neighbor))

    return None, 0  # Pas de solution
