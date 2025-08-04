import uuid
from domain.model.game_matrix import GameMatrix


class GameServer:
    """
    Класс, управляющий игровым процессом на стороне сервера.
    Содержит информацию об игровом поле, игроках, типе игры и текущем состоянии игры.
    """

    # Константы для кодов ошибок
    ERR_CODE = {
        'GAME OVER': 101,  # Игра завершена
        'CELL NOT EMPTY': 102  # Ячейка уже занята
    }

    # Константы для состояний игры
    GAME_STATE = {
        'DRAW': 0,  # Ничья
        'CURRENT PLAYER1 WIN': -1,  # Победа первого игрока
        'CURRENT PLAYER2 WIN': 1,  # Победа второго игрока
        'WAIT PLAYERS': 200,  # Ожидание игроков
        'CURRENT PLAYER1 MOVE': 201,  # Ход первого игрока
        'CURRENT PLAYER2 MOVE': 202  # Ход второго игрока
    }

    # Константы для типов игры
    GAME_TYPE = {
        'MACHINE': 1,  # Игра против машины
        'PLAYER': 2  # Игра против другого игрока
    }

    # Маркеры игроков
    PLAYER_ONE_MARKER = 1  # Маркер первого игрока (например, "X")
    PLAYER_TWO_MARKER = 2  # Маркер второго игрока (например, "O")

    def __init__(self, rows=1, cols=1, game_uuid=None, game_type=1,
                 current_player1=None, current_player2=None, status=None):
        """
        Инициализация игрового сервера.

        :param rows: Количество строк на игровом поле (по умолчанию 1).
        :param cols: Количество столбцов на игровом поле (по умолчанию 1).
        :param game_uuid: Уникальный идентификатор игры (генерируется автоматически, если не указан).
        :param game_type: Тип игры (1 — против машины, 2 — против игрока).
        :param current_player1: UUID первого игрока (может быть None, если игра еще не началась).
        :param current_player2: UUID второго игрока (может быть None, если игра еще не началась).
        :param status: Текущий статус игры (по умолчанию None).
        """
        self.board = GameMatrix(rows, cols)  # Игровое поле (пустое)
        self.UUID = game_uuid if game_uuid else str(uuid.uuid4())  # Уникальный идентификатор игры
        self.current_player1 = current_player1  # UUID первого игрока
        self.current_player2 = current_player2  # UUID второго игрока
        self.status = status  # Текущий статус игры
        self.game_type = game_type  # Тип игры (1 — против машины, 2 — против игрока)

    def __repr__(self):
        """
        Представление объекта для отладки.

        :return: Строковое представление объекта GameServer.
        """
        return (f"GameServer(UUID={self.UUID}, "
                f"game_type={self.game_type}, "
                f"status={self.status}, "
                f"current_player1={self.current_player1}, "
                f"current_player2={self.current_player2})")
