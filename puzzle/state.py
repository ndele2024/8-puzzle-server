from typing import List, Tuple, Optional
import random
from dataclasses import dataclass

@dataclass
class PuzzleState:
  """
    classe représentant l'état du puzzle a un instant
  """
  board: List[List[int]]
  empty_position: Tuple[int, int]
  parent: Optional['PuzzleState'] = None
  cost : int = 0
  move : Optional[str] = None  # "UP", "DOWN", "LEFT", "RIGHT"

  def __empty_cellule_position__(self) -> tuple[int, int] | None:
    """
      Retourne la position de la case vide
    """
    for i in range(len(self.board)):
      for j in range(len(self.board[i])):
        if self.board[i][j] == 0:
          return i, j
    return None

  #egalité entre deux états selon la matrice des cases
  def __eq__(self, other) -> bool:
    return self.board == other.board

  def __hash__(self):
    return hash(tuple(tuple(row) for row in self.board))
    #return hash(str(self.board))

  def __lt__(self, other):
    return self.cost < other.cost

  #génère l'état final recherché (deux état finaux possibles)
  #exemple pour une grille de 3*3 [[1, 2, 3], [4, 5, 6], [7, 8, 0]] ou [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
  def genarate_goal_state(self) -> List[List[int]]:
    n, m = len(self.board), len(self.board[0])
    goal_state1 = [[i * m + j for j in range(m)] for i in range(n)]
    goal_state2 = [[(i * m + j) % (n * m) for j in range(m)] for i in range(n)]
    #ici on doit retourner un tuple contenant les deux états finaux possibles (-------------à faire---------------)
    return goal_state1

  def is_goal(self) -> bool:
    """
      vérifie si l'état actuel est un état final
    """
    goal_state = self.genarate_goal_state()
    return self.board == goal_state

  def get_neighbors(self) -> List['PuzzleState']:
    """
      retourne une liste d'état enfant à partir de l'état actuel
    """
    neighbors = []
    row, col = self.empty_position
    moves = {
        "UP": (row - 1, col),
        "DOWN": (row + 1, col),
        "LEFT": (row, col - 1),
        "RIGHT": (row, col + 1)
    }

    for move, (r, c) in moves.items():
      if 0 <= r < 3 and 0 <= c < 3:
        new_board = [row[:] for row in self.board]
        new_board[row][col], new_board[r][c] = new_board[r][c], new_board[row][col]
        neighbors.append(PuzzleState(
            board = new_board,
            empty_position = (r, c),
            parent = self,
            move = move,
            cost = self.cost + 1
        ))
    return neighbors

  @staticmethod
  def generate_random_state(n = 3, m = 3) :
    #n, m = 3, 3
    numbers = list(range(n * m))
    random.shuffle(numbers)
    #on génère l'état
    board = [[numbers[i * m + j] for j in range(m)] for i in range(n)]

    #Vérification si le puzzle est solvable
    is_solvable, _ = PuzzleState.is_solvable_puzzle(board)
    while not is_solvable:
      random.shuffle(numbers)
      # on génère l'état
      board = [[numbers[i * m + j] for j in range(m)] for i in range(n)]
      is_solvable, _ = PuzzleState.is_solvable_puzzle(board)

    # on trouve la position de la valeur 0
    pos_0 = -1
    for i in range(n * m):
      if numbers[i] == 0:
        pos_0 = i
        break
    # on convertit en tuple (i,j)
    empty_position = (pos_0 // m, pos_0 % m)
    return PuzzleState(board = board, empty_position = empty_position)

  @staticmethod
  def is_solvable_puzzle(board):
    n = len(board)
    flat_all = [x for row in board for x in row]
    flat = [x for x in flat_all if x != 0]

    inversions = 0
    for i in range(len(flat)):
      for j in range(i + 1, len(flat)):
        if flat[i] > flat[j]:
          inversions += 1

    if n % 2 == 1:
      # largeur impaire (3x3 par exemple)
      return inversions % 2 == 0, inversions

    # largeur paire: dépend de la ligne du zéro en partant du bas
    zero_index = flat_all.index(0)
    zero_row_from_top = zero_index // n
    zero_row_from_bottom = n - zero_row_from_top

    solvable = (inversions + zero_row_from_bottom) % 2 == 0

    return solvable, inversions