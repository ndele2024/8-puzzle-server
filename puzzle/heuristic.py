from abc import ABC, abstractmethod

from puzzle.state import PuzzleState


class IHeuristic(ABC):
  @abstractmethod
  def calculate(self, state: PuzzleState) -> int:
    """
      Evalue le cout restant estime pour atteindre l'etat final.
    """
    raise NotImplementedError


class ManhattanDistance(IHeuristic):
  def calculate(self, state: PuzzleState) -> int:
    distance = 0
    width = len(state.board[0])

    for i in range(len(state.board)):
      for j in range(len(state.board[i])):
        value = state.board[i][j]
        if value != 0:
          # On cible la meme grille finale que PuzzleState.generate_goal_state:
          # les tuiles 1..n sont rangees dans l'ordre, puis 0 en bas a droite.
          x_goal, y_goal = divmod(value - 1, width)
          distance += abs(i - x_goal) + abs(j - y_goal)

    return distance


class HammingDistance(IHeuristic):
  def calculate(self, state: PuzzleState) -> int:
    distance = 0
    goal = state.generate_goal_state()

    for i in range(len(state.board)):
      for j in range(len(state.board[i])):
        if state.board[i][j] != 0 and state.board[i][j] != goal[i][j]:
          distance += 1

    return distance
