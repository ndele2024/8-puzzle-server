import unittest
from unittest.mock import patch

from puzzle.state import PuzzleState


class TestPuzzleState(unittest.TestCase):
    def setUp(self):
        self.goal_state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            empty_position=(2, 2),
        )

    def test_empty_cellule_position_returns_coordinates_of_zero(self):
        # Ce test verifie que la recherche interne de la case vide retrouve bien
        # les coordonnees du 0 dans la grille courante.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 0, 5], [6, 7, 8]],
            empty_position=(1, 1),
        )

        self.assertEqual(state.__empty_cellule_position__(), (1, 1))

    def test_empty_cellule_position_returns_none_when_zero_is_missing(self):
        # Ce test couvre le cas defensif ou la grille ne contient aucun 0.
        # La methode doit alors signaler l'absence de case vide avec None.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            empty_position=(0, 0),
        )

        self.assertIsNone(state.__empty_cellule_position__())

    def test_validate_accepts_a_well_formed_board(self):
        # Ce test verifie que la validation laisse passer une grille correcte,
        # avec toutes les valeurs attendues et une position vide coherente.
        self.goal_state.validate()

    def test_validate_rejects_mismatched_empty_position(self):
        # Ce test documente l'erreur levee quand la position vide annoncee
        # ne correspond pas a l'emplacement reel du 0 dans la grille.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            empty_position=(0, 0),
        )

        with self.assertRaisesRegex(ValueError, "position vide"):
            state.validate()

    def test_equality_and_hash_depend_on_board_content(self):
        # Ce test garantit que deux etats avec la meme grille sont vus comme
        # identiques, ce qui est indispensable pour les ensembles `visited`.
        state_a = PuzzleState(
            board=[[1, 2, 3], [4, 0, 5], [6, 7, 8]],
            empty_position=(1, 1),
        )
        state_b = PuzzleState(
            board=[[1, 2, 3], [4, 0, 5], [6, 7, 8]],
            empty_position=(0, 0),
        )

        self.assertEqual(state_a, state_b)
        self.assertEqual(hash(state_a), hash(state_b))

    def test_lt_compares_costs(self):
        # Ce test confirme que l'ordre entre etats repose sur le cout,
        # ce qui est utilise par les files de priorite.
        cheaper = PuzzleState(board=[[0]], empty_position=(0, 0), cost=1)
        more_expensive = PuzzleState(board=[[0]], empty_position=(0, 0), cost=3)

        self.assertLess(cheaper, more_expensive)

    def test_generate_goal_state_matches_standard_solved_board(self):
        # Ce test documente la convention retenue apres correction:
        # l'etat final est 1..8 avec 0 en bas a droite.
        self.assertEqual(
            self.goal_state.generate_goal_state(),
            [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
        )

    def test_legacy_goal_method_keeps_same_result(self):
        # Ce test garantit que l'ancien nom de methode reste utilisable,
        # afin de ne pas casser le code existant pendant la transition.
        self.assertEqual(
            self.goal_state.genarate_goal_state(),
            self.goal_state.generate_goal_state(),
        )

    def test_is_goal_returns_true_for_generated_goal_board(self):
        # Ce test valide que l'etat reconnu comme final par l'application
        # correspond bien a la grille standard du puzzle resolu.
        self.assertTrue(self.goal_state.is_goal())

    def test_get_neighbors_returns_all_valid_moves_with_parent_and_cost(self):
        # Ce test verifie qu'un etat central produit 4 voisins valides
        # et que chaque voisin garde la trace du parent, du mouvement et du cout.
        state = PuzzleState(
            board=[[1, 2, 3], [4, 0, 5], [6, 7, 8]],
            empty_position=(1, 1),
            cost=2,
        )

        neighbors = state.get_neighbors()

        self.assertEqual(len(neighbors), 4)
        self.assertEqual(
            {neighbor.move for neighbor in neighbors},
            {"UP", "DOWN", "LEFT", "RIGHT"},
        )
        self.assertTrue(all(neighbor.parent is state for neighbor in neighbors))
        self.assertTrue(all(neighbor.cost == 3 for neighbor in neighbors))

    def test_get_neighbors_from_corner_returns_only_two_moves(self):
        # Ce test couvre une case vide dans un coin: seuls 2 deplacements
        # doivent etre possibles dans cette configuration.
        neighbors = self.goal_state.get_neighbors()

        self.assertEqual(len(neighbors), 2)
        self.assertEqual({neighbor.move for neighbor in neighbors}, {"UP", "LEFT"})

    def test_is_solvable_puzzle_returns_true_for_known_solvable_board(self):
        # Ce test s'assure qu'une configuration classique soluble est detectee
        # comme telle, avec un nombre d'inversions pair.
        solvable, inversions = PuzzleState.is_solvable_puzzle(
            [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        )

        self.assertTrue(solvable)
        self.assertEqual(inversions, 0)

    def test_is_solvable_puzzle_returns_false_for_known_unsolvable_board(self):
        # Ce test utilise un exemple standard impossible a resoudre:
        # l'echange de 7 et 8 cree un nombre d'inversions impair.
        solvable, inversions = PuzzleState.is_solvable_puzzle(
            [[1, 2, 3], [4, 5, 6], [8, 7, 0]]
        )

        self.assertFalse(solvable)
        self.assertEqual(inversions, 1)

    @patch("puzzle.state.random.shuffle")
    def test_generate_random_state_retries_until_board_is_solvable(self, mocked_shuffle):
        # Ce test force d'abord une grille impossible puis une grille soluble
        # pour verifier que la generation recommence tant que necessaire.
        sequences = [
            [1, 2, 3, 4, 5, 6, 8, 7, 0],
            [1, 2, 3, 4, 5, 6, 7, 8, 0],
        ]

        def fake_shuffle(numbers):
            numbers[:] = sequences.pop(0)

        mocked_shuffle.side_effect = fake_shuffle

        state = PuzzleState.generate_random_state()

        self.assertEqual(state.board, [[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(state.empty_position, (2, 2))
        self.assertEqual(mocked_shuffle.call_count, 2)


if __name__ == "__main__":
    unittest.main()
