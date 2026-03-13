import unittest

from puzzle.solver import PuzzleSolver
from puzzle.solver_strategy import BfsStrategy
from puzzle.state import PuzzleState


class TestPuzzleSolver(unittest.TestCase):
    def test_reconstruct_path_returns_moves_from_root_to_leaf(self):
        # Ce test verifie que le chemin reconstruit remonte correctement la
        # chaine des parents puis restitue les mouvements dans le bon ordre.
        root = PuzzleState(board=[[0, 1], [2, 3]], empty_position=(0, 0))
        child = PuzzleState(
            board=[[1, 0], [2, 3]],
            empty_position=(0, 1),
            parent=root,
            move="RIGHT",
            cost=1,
        )
        leaf = PuzzleState(
            board=[[1, 3], [2, 0]],
            empty_position=(1, 1),
            parent=child,
            move="DOWN",
            cost=2,
        )

        path = PuzzleSolver(BfsStrategy()).reconstruct_path(leaf)

        self.assertEqual(path, ["RIGHT", "DOWN"])

    def test_reconstruct_path_returns_empty_list_for_root_state(self):
        # Ce test couvre le cas d'un etat initial sans parent:
        # aucun mouvement n'est necessaire pour l'atteindre.
        root = PuzzleState(board=[[0, 1], [2, 3]], empty_position=(0, 0))

        path = PuzzleSolver(BfsStrategy()).reconstruct_path(root)

        self.assertEqual(path, [])


if __name__ == "__main__":
    unittest.main()
