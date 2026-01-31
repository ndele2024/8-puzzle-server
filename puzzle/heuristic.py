from puzzle.state import PuzzleState


class IHeuristic:
  def calculate(self, state: PuzzleState) -> int:
    pass


class ManhattanDistance(IHeuristic):
  def calculate(self, state: PuzzleState) -> int:
    distance = 0
    for i in range(len(state.board)):
      for j in range(len(state.board[i])):
        if state.board[i][j] != 0:
          x_goal, y_goal = divmod(state.board[i][j] - 1, len(state.board))
          distance += abs(i - x_goal) + abs(j - y_goal)
    return distance


class HammingDistance(IHeuristic):
  def calculate(self, state: PuzzleState) -> int:
    distance = 0
    goal = state.genarate_goal_state()
    for i in range(len(state.board)):
      for j in range(len(state.board[i])):
        if state.board[i][j] != 0 and state.board[i][j] != goal[i][j]:
          distance += 1
    return distance
