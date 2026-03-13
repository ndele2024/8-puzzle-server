from typing import List, Tuple, Optional
import random
from dataclasses import dataclass


@dataclass
class PuzzleState:
  """
    classe representant l'etat du puzzle a un instant
  """
  board: List[List[int]]
  empty_position: Tuple[int, int]
  parent: Optional['PuzzleState'] = None
  cost: int = 0
  move: Optional[str] = None  # "UP", "DOWN", "LEFT", "RIGHT"

  def __empty_cellule_position__(self) -> tuple[int, int] | None:
    """
      Retourne la position de la case vide
    """
    for i in range(len(self.board)):
      for j in range(len(self.board[i])):
        if self.board[i][j] == 0:
          return i, j
    return None

  def validate(self) -> None:
    """
      Verifie que la grille est bien formee et que `empty_position`
      correspond reellement a la case vide.
    """
    if not self.board or not self.board[0]:
      raise ValueError("La grille ne peut pas etre vide.")

    row_length = len(self.board[0])
    if any(len(row) != row_length for row in self.board):
      raise ValueError("Toutes les lignes de la grille doivent avoir la meme taille.")

    expected_values = list(range(len(self.board) * row_length))
    actual_values = sorted(x for row in self.board for x in row)
    if actual_values != expected_values:
      raise ValueError("La grille doit contenir exactement les valeurs de 0 a n*m-1.")

    actual_empty_position = self.__empty_cellule_position__()
    if actual_empty_position != self.empty_position:
      raise ValueError("La position vide fournie ne correspond pas a la case 0 de la grille.")

  # egalite entre deux etats selon la matrice des cases
  def __eq__(self, other) -> bool:
    return self.board == other.board

  def __hash__(self):
    return hash(tuple(tuple(row) for row in self.board))

  def __lt__(self, other):
    return self.cost < other.cost

  def generate_goal_state(self) -> List[List[int]]:
    """
      Genere l'etat final de reference du puzzle:
      1..(n*m-1) avec 0 en bas a droite.
    """
    n, m = len(self.board), len(self.board[0])
    values = list(range(1, n * m)) + [0]
    return [[values[i * m + j] for j in range(m)] for i in range(n)]

  # Conserve l'ancien nom pour ne pas casser le reste du projet.
  def genarate_goal_state(self) -> List[List[int]]:
    return self.generate_goal_state()

  def is_goal(self) -> bool:
    """
      verifie si l'etat actuel est un etat final
    """
    return self.board == self.generate_goal_state()

  def get_neighbors(self) -> List['PuzzleState']:
    """
      retourne une liste d'etat enfant a partir de l'etat actuel
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
      if 0 <= r < len(self.board) and 0 <= c < len(self.board[0]):
        new_board = [current_row[:] for current_row in self.board]
        new_board[row][col], new_board[r][c] = new_board[r][c], new_board[row][col]
        neighbors.append(PuzzleState(
            board=new_board,
            empty_position=(r, c),
            parent=self,
            move=move,
            cost=self.cost + 1
        ))
    return neighbors

  @staticmethod
  def generate_random_state(n=3, m=3):
    numbers = list(range(n * m))
    random.shuffle(numbers)
    board = [[numbers[i * m + j] for j in range(m)] for i in range(n)]

    is_solvable, _ = PuzzleState.is_solvable_puzzle(board)
    while not is_solvable:
      random.shuffle(numbers)
      board = [[numbers[i * m + j] for j in range(m)] for i in range(n)]
      is_solvable, _ = PuzzleState.is_solvable_puzzle(board)

    pos_0 = numbers.index(0)
    empty_position = (pos_0 // m, pos_0 % m)
    return PuzzleState(board=board, empty_position=empty_position)

  @staticmethod
  def is_solvable_puzzle(board):
    n = len(board)
    m = len(board[0])
    flat_all = [x for row in board for x in row]
    flat = [x for x in flat_all if x != 0]

    inversions = 0
    for i in range(len(flat)):
      for j in range(i + 1, len(flat)):
        if flat[i] > flat[j]:
          inversions += 1

    if m % 2 == 1:
      # Largeur impaire: le puzzle est soluble quand le nombre d'inversions est pair.
      return inversions % 2 == 0, inversions

    # Largeur paire: on tient compte de la ligne du zero en partant du bas.
    zero_index = flat_all.index(0)
    zero_row_from_top = zero_index // m
    zero_row_from_bottom = n - zero_row_from_top
    solvable = (inversions + zero_row_from_bottom) % 2 == 0

    return solvable, inversions
