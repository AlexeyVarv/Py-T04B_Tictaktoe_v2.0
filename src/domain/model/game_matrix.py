class GameMatrix:
    def __init__(self, rows=1, cols=1):
        self.game_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
