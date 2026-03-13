import unittest

from puzzle.heuristic import HammingDistance, ManhattanDistance
from puzzle.state import PuzzleState


class TestHeuristics(unittest.TestCase):
    def test_manhattan_distance_returns_zero_for_goal_state(self):
        # Ce test verifie que Manhattan est maintenant alignee avec l'etat
        # final officiel du projet: 1..8 puis 0.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            empty_position=(2, 2),
        )

        self.assertEqual(ManhattanDistance().calculate(state), 0)

    def test_manhattan_distance_counts_sum_of_tile_distances(self):
        # Ce test documente un cas simple: seule la tuile 8 est decalee
        # d'une case par rapport a sa position cible.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            empty_position=(2, 1),
        )

        self.assertEqual(ManhattanDistance().calculate(state), 1)

    def test_hamming_distance_returns_zero_for_goal_state(self):
        # Ce test confirme que Hamming utilise le meme etat final que Manhattan,
        # afin d'eviter des heuristiques qui se contredisent.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            empty_position=(2, 2),
        )

        self.assertEqual(HammingDistance().calculate(state), 0)

    def test_hamming_distance_counts_only_misplaced_non_zero_tiles(self):
        # Ce test verifie que le 0 est ignore et que seules les tuiles mal
        # positionnees augmentent la distance de Hamming.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            empty_position=(2, 1),
        )

        self.assertEqual(HammingDistance().calculate(state), 1)


if __name__ == "__main__":
    unittest.main()
