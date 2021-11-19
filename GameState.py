import collections
import random


class GameState:
    no_rows = 5
    no_cols = 5

    def __init__(self, lights_on):
        self.lights_on = lights_on
        self.shortest_solution = None

    def is_winning(self):
        return all(not any(map(bool, lights_row)) for lights_row in self.lights_on)

    def switch_light(self, x, y):
        assert 0 <= x < GameState.no_rows and 0 <= y < GameState.no_cols
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

    def define_solutions(self, solutions):
        shortest_solution_length = GameState.no_cols * GameState.no_rows + 1
        for solution in solutions:
            assert len(solution) == GameState.no_rows
            assert len(solution[0]) == GameState.no_cols
            solution_length = sum([toggle for sublist in solution for toggle in sublist])
            if solution_length < shortest_solution_length:
                shortest_solution_length = solution_length
                self.shortest_solution = solution

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

    def has_shortest_solution(self):
        return self.shortest_solution is not None

    def __toggle_light(self, x, y):
        self.lights_on[x][y] = 1 - self.lights_on[x][y]
