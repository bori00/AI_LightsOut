import random
from copy import deepcopy

"""
Class representing the current state of the current game session.

Note that a game may consists of multiple game sessions, i.e. of multiple puzzles.
"""


class GameState:
    no_rows = 5
    no_cols = 5

    """
    Constructor
    
    lights_on: a list of list of integers, each with the value 0 or 1, representing the initial state of the light 
    bulbs (0=Off, 1=On). 
    """

    def __init__(self, lights_on):
        self.initial_lights_on = deepcopy(lights_on)
        self.lights_on = lights_on
        self.shortest_solution = None
        self.__no_steps = 0;

    """
    Returns true if and only if the game is won.
    """

    def is_winning(self):
        return all(not any(map(bool, lights_row)) for lights_row in self.lights_on)

    """
    Switches the light bulb in position (x, y).
    
    As a consequence, the state of the light bulbs adjacent to the switched bulb is toggled too.
    
    If this step is not part of the currently known shortest path to a winning state, then the shortest_solution is 
    deleted. Else, it is updated, with the current step being removed from it. 
    
    Note that the positions are indexed from 0.
    X: the row of the light bulb to switch.
    y; the column of the light bulb to switch.
    """

    def switch_light(self, x, y):
        assert 0 <= x < GameState.no_rows and 0 <= y < GameState.no_cols
        self.__no_steps = self.__no_steps + 1
        self.__toggle_light(x, y)
        if x > 0:
            self.__toggle_light(x - 1, y)
        if x + 1 < GameState.no_rows:
            self.__toggle_light(x + 1, y)
        if y > 0:
            self.__toggle_light(x, y - 1)
        if y + 1 < GameState.no_cols:
            self.__toggle_light(x, y + 1)
        if self.shortest_solution is not None:
            if self.shortest_solution[x][y] == 1:
                self.shortest_solution[x][y] = 0.
            else:
                self.shortest_solution = None

    """
    Informs the GameState about the solutions for the problem from the current state.
    
    Based on the solutions (it can be mathematically proved, that there are 4 of them), the shortest one is selected 
    and cached. 
    
    solutions: a list of solution matrices. Each solution matrix is a list of lists of integers, with a 1 on position 
    (x, y) if the light bulb on position (x, y) needs to be toggled, and 0 otherwise. 
    """

    def set_solutions(self, solutions):
        shortest_solution_length = GameState.no_cols * GameState.no_rows + 1
        for solution in solutions:
            assert len(solution) == GameState.no_rows
            assert len(solution[0]) == GameState.no_cols
            solution_length = sum([toggle for sublist in solution for toggle in sublist])
            if solution_length < shortest_solution_length:
                shortest_solution_length = solution_length
                self.shortest_solution = solution

    """
    If previously the solutions for the game were specified, then returns a step (x, y) meaning that by switching 
    the light bulb on position (x, y) the winning state will be 1 step closer. If no solutions are known, 
    returns None. 
    """

    def get_hint_for_next_step(self):
        if self.shortest_solution is not None:
            solution_vector = [toggle for sublist in self.shortest_solution for toggle in sublist]
            required_steps = [i for i, toggle in enumerate(solution_vector) if toggle == 1]
            hinted_step_vector_index = random.choice(required_steps)
            hinted_step_row = hinted_step_vector_index / GameState.no_cols
            hinted_step_col = hinted_step_vector_index % GameState.no_cols
            hinted_step_matrix_index = (hinted_step_row, hinted_step_col)
            return hinted_step_matrix_index
        else:
            return None

    """
    Returns true if and only if the shortest solution to the winning state from the current state is known. 
    Otherwise false. 
    """

    def has_shortest_solution(self):
        return self.shortest_solution is not None

    """
    Resets the game to its initial state.
    """

    def reset_to_initial_state(self):
        self.lights_on = deepcopy(self.initial_lights_on)
        self.shortest_solution = None
        self.__no_steps = 0

    def get_total_no_steps(self):
        return self.__no_steps

    def __toggle_light(self, x, y):
        self.lights_on[x][y] = 1 - self.lights_on[x][y]
