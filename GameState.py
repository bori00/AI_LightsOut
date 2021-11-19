class GameState:
    no_rows = 5
    no_cols = 5

    def __init__(self, lights_on):
        self.lights_on = lights_on

    def is_winning(self):
        return all(not any(lights_row) for lights_row in self.lights_on)

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

    def __toggle_light(self, x, y):
        self.lights_on[x][y] = not self.lights_on[x][y]


game_state = GameState([[False, False, False, False],
                        [False, False, False, False],
                        [False, False, False, False],
                        [False, False, True, True, True],
                        [False, True, False, True, False]])
print game_state.is_winning()
game_state.switch_light(4, 2)
game_state.switch_light(4, 3)
print game_state.is_winning()
game_state.switch_light(4, 4)
print game_state.is_winning()

game_state2 = GameState([[False, False, False, False],
                         [False, False, False, False],
                         [False, False, False, False],
                         [False, False, False, False],
                         [False, False, False, False]])
print game_state2.is_winning()
