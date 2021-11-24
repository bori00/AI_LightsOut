import os
import random
import sys
from copy import deepcopy

from GameState import GameState

"""
Class responsible for the logic of the game: 
- it stores and updates the game state
- generates puzzles and solved them using system calls to mace4.

All communication between the controller and the service layer should be done via the GameService, and the controller 
should never access the game state directly. 
"""


class GameService:
    NO_GAME_MODELS = 1000

    """
    Initializes the game and starts the first game session.
    
    To do this, it generates a list of random solvable puzzles and picks one of them as the starting game session.
    """

    def __init__(self):
        self.__generate_random_games(GameService.NO_GAME_MODELS)
        self.__game_models = self.__get_generated_game_models()
        self.__played_games = []
        self.__game_state = None
        self.init_new_game_session()
        self.__set_game_session_solutions()

    """Starts a new game session, with a puzzle that was not used before in this game, unless all puzzles have 
    already been used. """

    def init_new_game_session(self):
        if len(self.__played_games) == GameService.NO_GAME_MODELS:
            self.__played_games = []
        game_model_index = random.randint(0, GameService.NO_GAME_MODELS - 1)
        while game_model_index in self.__played_games:
            game_model_index = random.randint(0, GameService.NO_GAME_MODELS - 1)
        self.__played_games.append(game_model_index)
        self.__game_state = GameState(deepcopy(self.__game_models[game_model_index]))

    """
    Returns true if and only if the current game session was won.
    """

    def won_game_session(self):
        return self.__game_state.is_winning()

    """
    Switches the light bulb in position (x, y) (indexed from 0) for the current game session.
    """

    def switch_light(self, x, y):
        self.__game_state.switch_light(x, y)

    """
    Returns the state of all light bulbs in the current game session, in the format of a list of lists of integers, 
    where result[x][y] = 1 if the light bulb on position (x, y) is on, and 0 otherwise.
    """

    def get_lights_state(self):
        return self.__game_state.get_lights_state()

    """
    Returns a step represented by a tuple with two integers, (x, y), meaning that by switching the light bulb on 
    position (x, y) the winning state will be 1 step closer.
    """

    def get_hint(self):
        if self.__game_state.has_shortest_solution():
            return self.__game_state.get_hint_for_next_step()
        else:
            self.__set_game_session_solutions()
            return self.__game_state.get_hint_for_next_step()

    """
    Resets the game session to its original state.
    """

    def reset_game_session(self):
        self.__game_state.reset_to_initial_state()

    """
    Returns the number of steps taken since the last game session was started/reset to its initial state.
    """

    def get_no_steps_in_game_session(self):
        return self.__game_state.get_total_no_steps()

    """
    Returns the number of steps in the shortest solution from the initial state to the winning state.
    """
    def length_of_shortest_solution_from_initial_state(self):
        return self.__game_state.length_of_shortest_solution_from_initial_state()

    def __set_game_session_solutions(self):
        game_solutions = map(self.__cut_first_last_row_col, self.__generate_game_solutions())
        self.__game_state.set_solutions(game_solutions)

    def __generate_game_solutions(self):
        try:
            with open("GameSolutions/allout_solver_template.in") as template_file:
                solver_template = template_file.read()
                solver_mace4_code = solver_template.format(On=self.__generate_game_state_propositions_string())
                with open("GameSolutions/allout_solver.in", "w") as solver_file:
                    solver_file.write(solver_mace4_code)
                    solver_file.flush()
                    os.system("mace4 -m -1 -f GameSolutions/allout_solver.in | "
                              "interpformat portable > GameSolutions/allout_solutions.out")
                    with open("GameSolutions/allout_solutions.out") as solutions_file:
                        solutions_data = eval(solutions_file.read())
                        solutions = map(self.__transform_solution_data, solutions_data)
                        return solutions
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:  # handle other exceptions such as attribute errors
            print "Unexpected error:", sys.exc_info()[0]
        sys.exit(1)


    def __get_generated_game_models(self):
        f = open("GameModels/allout_math_efficient_generated.out")
        game_models_data = eval(f.read())
        game_models = map(self.__transform_game_model_data, game_models_data)
        return game_models

    def __generate_game_state_propositions_string(self):
        lights_state = self.__game_state.get_lights_state()
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

    def __cut_first_last_row_col(self, matrix):
        matrix.pop(0)
        matrix.pop(len(matrix) - 1)
        for row in matrix:
            row.pop(0)
            row.pop(len(row) - 1)
        return matrix

    @staticmethod
    def __generate_random_games(no_game_models):
        os.system("mace4 -m {nr_game_models} -f GameModels/allout_math_efficient_generator.in  | "
                  "interpformat portable > GameModels/allout_math_efficient_generated.out".format(
            nr_game_models=no_game_models))

    @staticmethod
    def __transform_game_model_data(game_model_data):
        game_extracted_model = game_model_data[2][7][3]
        return game_extracted_model

    @staticmethod
    def __transform_solution_data(solution_data):
        extracted_solution = solution_data[2][1][3]
        return extracted_solution


#TODO: remove this code before submitting assignment
# This code demonstrates the behavior of the service layer
game_service = GameService()
for i in range(3):
    print "----------------------------------------INIT STATE------------------------------------------------"
    print game_service._GameService__game_state._GameState__lights_on
    print "Game shortest solution:"
    print game_service._GameService__game_state._GameState__shortest_solution
    while not game_service.won_game_session():
        p = random.uniform(0, 1)
        # Take the correct step with a probability of 80%, and a random step with probability 20%
        # With prob 1% reset the game
        if p <= 0.1:
            game_service.reset_game_session()
            print "----------------------------------------RESET GAME------------------------------------"
            print "Game state:"
            print game_service._GameService__game_state._GameState__lights_on
            print "Game shortest solution:"
            print game_service._GameService__game_state._GameState__shortest_solution
        elif p < 0.2:
            rand_step = (random.randint(0, 4), random.randint(0, 4))
            game_service.switch_light(rand_step[0], rand_step[1])
            print "-------Random Step: ", rand_step
            print "Game state:"
            print game_service._GameService__game_state._GameState__lights_on
            print "Game shortest solution:"
            print game_service._GameService__game_state._GameState__shortest_solution
        else:
            hint = game_service.get_hint()
            game_service.switch_light(hint[0], hint[1])
            print "------------Step: ", hint
            print "Game state:"
            print game_service._GameService__game_state._GameState__lights_on
            print "Game shortest solution:"
            print game_service._GameService__game_state._GameState__shortest_solution
    print "No steps: " + str(game_service.get_no_steps_in_game_session())
    print "Min no steps: " + str(game_service.length_of_shortest_solution_from_initial_state())
    game_service.init_new_game_session()
