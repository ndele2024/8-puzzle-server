import heapq
from typing import Tuple, Any
from abc import abstractmethod, ABC

from puzzle.heuristic import IHeuristic
from puzzle.state import PuzzleState


# Interface strategy for all differents solvers methods
class IsolverStrategy(ABC):
  @abstractmethod
  def solve(self, initial_state: PuzzleState) -> Tuple[PuzzleState, int]:
    pass


class BfsStrategy(IsolverStrategy):
  def solve(self, initial_state: PuzzleState) -> tuple[PuzzleState, int] | tuple[None, int]:
    queue = [initial_state]
    visited = {initial_state}

    while queue:
      current = queue.pop(0)
      if current.is_goal():
        return current, current.cost

      for neighbor in current.get_neighbors():
        if neighbor not in visited:
          visited.add(neighbor)
          queue.append(neighbor)

    return None, 0


class DfsStrategy(IsolverStrategy):
  def solve(self, initial_state: PuzzleState) -> Tuple[PuzzleState, int] | tuple[None, int]:
    stack = [initial_state]
    visited = {initial_state}

    while stack:
      current = stack.pop()
      if current.is_goal():
        return current, current.cost

      # On empile seulement les voisins jamais vus. Comme la pile depile le
      # dernier element ajoute, conserver l'ordre natif permet d'explorer un
      # voisin direct pertinent avant de partir dans une branche tres profonde.
      for neighbor in current.get_neighbors():
        if neighbor not in visited:
          visited.add(neighbor)
          stack.append(neighbor)

    return None, 0


class AstarStrategy(IsolverStrategy):
  heuristic: IHeuristic

  def __init__(self, heurist: IHeuristic):
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

    return None, 0


class IdaStarStrategy(IsolverStrategy):
  heuristic: IHeuristic

  def __init__(self, heuristic: IHeuristic):
    self.heuristic = heuristic

  def solve(self, initial_state: PuzzleState):
    threshold = self.heuristic.calculate(initial_state)

    while True:
      temp = self.search(initial_state, 0, threshold, set())

      if isinstance(temp, PuzzleState):
        return temp, temp.cost

      if temp == float("inf"):
        return None, 0

      threshold = temp

  def search(self, state, g, threshold, path_states):
    f = g + self.heuristic.calculate(state)

    if f > threshold:
      return f

    if state.is_goal():
      return state

    minimum = float("inf")
    new_path_states = set(path_states)
    new_path_states.add(state)

    for neighbor in state.get_neighbors():
      if neighbor in new_path_states:
        continue

      temp = self.search(neighbor, g + 1, threshold, new_path_states)

      if isinstance(temp, PuzzleState):
        return temp

      if temp < minimum:
        minimum = temp

    return minimum
