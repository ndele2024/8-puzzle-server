import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient
    from puzzle.heuristic import HammingDistance, ManhattanDistance
    from puzzle.puzzle_controler import app, get_heuristic
    from puzzle.state import PuzzleState
    FASTAPI_AVAILABLE = True
except ModuleNotFoundError:
    TestClient = None
    HammingDistance = None
    ManhattanDistance = None
    app = None
    get_heuristic = None
    PuzzleState = None
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi non installe dans cet interpreteur")
class TestPuzzleControllerIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.one_move_payload = {
            "initial_state": [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            "empty_position": [2, 1],
            "algorithm": "all",
            "heuristic": "manhattan",
        }

    def test_get_heuristic_returns_manhattan_when_requested(self):
        # Ce test securise la petite fabrique d'heuristique utilisee
        # par les endpoints A* et IDA*.
        heuristic = get_heuristic("manhattan")

        self.assertIsInstance(heuristic, ManhattanDistance)

    def test_get_heuristic_is_case_insensitive(self):
        # Ce test documente la correction apportee: l'API accepte maintenant
        # Manhattan meme si la casse varie dans la requete client.
        heuristic = get_heuristic("ManHaTtAn")

        self.assertIsInstance(heuristic, ManhattanDistance)

    def test_get_heuristic_falls_back_to_hamming_for_other_values(self):
        # Ce test documente le comportement par defaut actuel:
        # toute autre valeur retourne Hamming.
        heuristic = get_heuristic("autre")

        self.assertIsInstance(heuristic, HammingDistance)

    def test_solve_endpoint_returns_all_algorithms_results(self):
        # Ce test verifie l'integration complete de l'endpoint principal:
        # parsing de la requete, execution des solveurs et structure de reponse.
        response = self.client.post("/solve", json=self.one_move_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"solutionBFS", "solutionDFS", "solutionAStar", "solutionIdastart"})
        self.assertEqual(body["solutionBFS"][0], ["RIGHT"])
        self.assertEqual(body["solutionBFS"][1], 1)
        self.assertEqual(body["solutionDFS"][1], 1)
        self.assertEqual(body["solutionAStar"][1], 1)
        self.assertEqual(body["solutionIdastart"][1], 1)

    def test_solve_bfs_endpoint_returns_only_bfs_result(self):
        # Ce test isole l'endpoint BFS pour verifier qu'il retourne
        # bien seulement la cle attendue avec un chemin valide.
        response = self.client.post("/solveBFS", json=self.one_move_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"solutionBFS"})
        self.assertEqual(body["solutionBFS"][0], ["RIGHT"])
        self.assertEqual(body["solutionBFS"][1], 1)

    def test_solve_dfs_endpoint_returns_only_dfs_result(self):
        # Ce test valide l'endpoint DFS et son contrat de reponse dedie.
        response = self.client.post("/solveDFS", json=self.one_move_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"solutionDFS"})
        self.assertEqual(body["solutionDFS"][1], 1)

    def test_solve_astar_endpoint_uses_requested_heuristic(self):
        # Ce test couvre l'endpoint A* avec l'heuristique Manhattan afin de
        # verifier que la reponse finale reste coherente cote API.
        response = self.client.post("/solveAStar", json=self.one_move_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"solutionAStar"})
        self.assertEqual(body["solutionAStar"][0], ["RIGHT"])
        self.assertEqual(body["solutionAStar"][1], 1)

    def test_solve_idastar_endpoint_returns_expected_result(self):
        # Ce test verifie l'endpoint IDA* sur la meme entree simple pour
        # securiser le branchement HTTP vers la strategie IDA*.
        response = self.client.post("/solveIdaStar", json=self.one_move_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"solutionIdastart"})
        self.assertEqual(body["solutionIdastart"][0], ["RIGHT"])
        self.assertEqual(body["solutionIdastart"][1], 1)

    def test_solve_bfs_returns_400_when_empty_position_is_incorrect(self):
        # Ce test met en evidence la nouvelle validation commune: si la case 0
        # n'est pas a la position annoncee, l'API refuse la requete explicitement.
        invalid_payload = {
            "initial_state": [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            "empty_position": [0, 0],
            "algorithm": "bfs",
            "heuristic": "manhattan",
        }

        response = self.client.post("/solveBFS", json=invalid_payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("position vide", response.json()["detail"])

    @patch("puzzle.puzzle_controler.PuzzleState.generate_random_state")
    def test_random_puzzle_endpoint_returns_generated_state(self, mocked_generate):
        # Ce test verifie que l'endpoint de generation aleatoire expose
        # correctement la grille et la position produites par le modele.
        mocked_generate.return_value = PuzzleState(
            board=[[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            empty_position=(2, 2),
        )

        response = self.client.get("/random_puzzle")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"initial_state": [[1, 2, 3], [4, 5, 6], [7, 8, 0]], "empty_position": [2, 2]},
        )


if __name__ == "__main__":
    unittest.main()
