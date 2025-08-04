class Game:
    def __init__(self, uuid=None):
        self.board = [''] * 9  # Игровое поле (пустое)
        self.UUID = uuid  # Уникальный идентификатор игры

