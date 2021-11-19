import os
import random
import sys
from copy import deepcopy

from GameState import GameState


def _generate_random_games(no_game_models):
    os.system("mace4 -m {nr_game_models} -f GameModels/allout_math_efficient_generator.in  | "
              "interpformat portable > GameModels/allout_math_efficient_generated.out".format(
        nr_game_models=no_game_models))


def transform_game_model_data(game_model_data):
    game_extracted_model = game_model_data[2][7][3]
    return game_extracted_model


def transform_solution_data(solution_data):
    extracted_solution = solution_data[2][1][3]
    return extracted_solution


class GameService:
    NO_GAME_MODELS = 1000

    def __init__(self):
        _generate_random_games(GameService.NO_GAME_MODELS)
        self._game_models = self._get_games_array()
        self._played_games = []
        self.game_state = None
        self.init_new_game()

    def init_new_game(self):
        if len(self._played_games) == GameService.NO_GAME_MODELS:
            self._played_games = []
        game_model_index = random.randint(0, GameService.NO_GAME_MODELS - 1)
        while game_model_index in self._played_games:
            game_model_index = random.randint(0, GameService.NO_GAME_MODELS - 1)
        self._played_games.append(game_model_index)
        self.game_state = GameState(deepcopy(self._game_models[game_model_index]))

    def won_game(self):
        return self.game_state.is_winning()

    def switch_light(self, x, y):
        self.game_state.switch_light(x, y)

    def get_hint(self):
        if self.game_state.has_shortest_solution():
            return self.game_state.get_hint_for_next_step()
        else:
            game_solutions = map(self.cut_first_last_row_col, self._generate_game_solutions())
            self.game_state.define_solutions(game_solutions)
            return self.game_state.get_hint_for_next_step()

    def _generate_game_solutions(self):
        try:
            with open("GameSolutions/allout_solver_template.in") as template_file:
                solver_template = template_file.read()
                solver_mace4_code = solver_template.format(On=self._generate_game_state_propositions_string())
                with open("GameSolutions/allout_solver.in", "w") as solver_file:
                    solver_file.write(solver_mace4_code)
                    solver_file.flush()
                    os.system("mace4 -m -1 -f GameSolutions/allout_solver.in | "
                              "interpformat portable > GameSolutions/allout_solutions.out")
                    with open("GameSolutions/allout_solutions.out") as solutions_file:
                        solutions_data = eval(solutions_file.read())
                        solutions = map(transform_solution_data, solutions_data)
                        return solutions
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:  # handle other exceptions such as attribute errors
            print "Unexpected error:", sys.exc_info()[0]
        sys.exit(1)

    def _get_games_array(self):
        f = open("GameModels/allout_math_efficient_generated.out")
        game_models_data = eval(f.read())
        game_models = map(transform_game_model_data, game_models_data)
        return game_models

    def _generate_game_state_propositions_string(self):
        lights_state = deepcopy(self.game_state.lights_on)
        lights_state_propositions = []
        lights_state.append([0] * GameState.no_cols)
        lights_state.insert(0, [0] * GameState.no_cols)
        for row, lights_row in enumerate(lights_state):
            lights_row.insert(0, 0)
            lights_row.append(0)
            for col, light_on in enumerate(lights_row):
                lights_state_propositions.append(
                    "On({row}, {col})={on}.".format(row=row, col=col, on=light_on))
        return "\n".join(lights_state_propositions)

    def cut_first_last_row_col(self, matrix):
        matrix.pop(0)
        matrix.pop(len(matrix) - 1)
        for row in matrix:
            row.pop(0)
            row.pop(len(row) - 1)
        return matrix


# This code demonstrates the behavior of the service layer
game_service = GameService()
for i in range(3):
    print "----------------------------------------INIT STATE----------------------------------"
    print game_service.game_state.lights_on
    while not game_service.won_game():
        p = random.uniform(0, 1)
        # Take the correct step with a probability of 80%, and a random step with probability 20%
        if p < 0.2:
            rand_step = (random.randint(0, 4), random.randint(0, 4))
            game_service.switch_light(rand_step[0], rand_step[1])
            print "-------Random Step: ", rand_step
            print "Game state:"
            print game_service.game_state.lights_on
            print "Game shortest solution:"
            print game_service.game_state.shortest_solution
        else:
            hint = game_service.get_hint()
            game_service.switch_light(hint[0], hint[1])
            print "------------Step: ", hint
            print "Game state:"
            print game_service.game_state.lights_on
            print "Game shortest solution:"
            print game_service.game_state.shortest_solution

    game_service.init_new_game()
