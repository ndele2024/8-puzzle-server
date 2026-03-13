import unittest

from puzzle.heuristic import HammingDistance, ManhattanDistance
from puzzle.solver_strategy import AstarStrategy, BfsStrategy, DfsStrategy, IdaStarStrategy
from puzzle.state import PuzzleState


class TestSolverStrategies(unittest.TestCase):
    def setUp(self):
        self.one_move_from_goal = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            empty_position=(2, 1),
        )
        self.unsolvable = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [8, 7, 0]],
            empty_position=(2, 2),
        )

    def test_bfs_finds_goal_and_reports_minimum_cost_on_simple_board(self):
        # Ce test verifie que BFS resout un puzzle tres simple et retrouve
        # le cout minimal attendu sur un cas a un seul mouvement du but.
        final_state, cost = BfsStrategy().solve(self.one_move_from_goal)

        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_goal())
        self.assertEqual(cost, 1)

    def test_dfs_finds_a_solution_on_simple_board(self):
        # Ce test valide que DFS atteint aussi un etat final sur une
        # configuration triviale, meme si sa strategie differe de BFS.
        final_state, cost = DfsStrategy().solve(self.one_move_from_goal)

        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_goal())
        self.assertEqual(cost, 1)

    def test_astar_with_manhattan_finds_solution_on_simple_board(self):
        # Ce test confirme qu'A* combine a Manhattan resout correctement
        # un cas simple en retournant un etat final coherent.
        final_state, cost = AstarStrategy(ManhattanDistance()).solve(self.one_move_from_goal)

        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_goal())
        self.assertEqual(cost, 1)

    def test_astar_with_hamming_finds_solution_on_simple_board(self):
        # Ce test rejoue le meme scenario avec Hamming pour securiser
        # la compatibilite entre la strategie A* et les deux heuristiques.
        final_state, cost = AstarStrategy(HammingDistance()).solve(self.one_move_from_goal)

        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_goal())
        self.assertEqual(cost, 1)

    def test_idastar_finds_solution_on_simple_board(self):
        # Ce test verifie que l'algorithme IDA* parvient lui aussi au but
        # sur un puzzle ou le chemin optimal est immediat.
        final_state, cost = IdaStarStrategy(ManhattanDistance()).solve(self.one_move_from_goal)

        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_goal())
        self.assertEqual(cost, 1)

    def test_bfs_returns_none_for_unsolvable_board(self):
        # Ce test documente le comportement attendu de BFS face a un puzzle
        # impossible: aucune solution n'est renvoyee.
        final_state, cost = BfsStrategy().solve(self.unsolvable)

        self.assertIsNone(final_state)
        self.assertEqual(cost, 0)


if __name__ == "__main__":
    unittest.main()
