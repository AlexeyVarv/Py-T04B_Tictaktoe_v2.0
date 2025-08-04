from abc import ABC, abstractmethod
from domain.model.game_server import GameServer

from abc import ABC, abstractmethod
from typing import Optional, Tuple

class GameService(ABC):
    """
    Абстрактный класс, управляющий игровым процессом.
    Определяет интерфейс для реализации игровой логики.
    """

    def __init__(self, game_server: 'GameServer'):
        """
        Инициализация сервиса игры.

        :param game_server: Объект, представляющий сервер игры.
        """
        self.game_server = game_server

    @abstractmethod
    def make_player_move(self, player_id: str, row_index: int, col_index: int) -> bool:
        """
        Сделать ход человека.

        :param player_id: UUID игрока, делающего ход.
        :param row_index: Индекс строки на игровом поле.
        :param col_index: Индекс столбца на игровом поле.
        :return: True, если ход успешен, иначе False.
        """
        pass

    @abstractmethod
    def make_machine_move(self):
        """
        Сделать ход машины.
        """
        pass

    @abstractmethod
    def verify_board(self, row_index: int, col_index: int) -> int | None:
        """
        Проверить корректность хода и что предыдущие ходы не изменены.

        :param row_index: Индекс строки на игровом поле.
        :param col_index: Индекс столбца на игровом поле.
        :return: Код ошибки (например, 102 — ячейка занята, 101 — игра окончена) или None.
        """
        pass

    @abstractmethod
    def check_winner(self) -> int | None:
        """
        Проверить победителя или ничью.

        :return: Состояние игры, определяющее результат или None если игра продолжается.
        """
        pass

    @abstractmethod
    def clean_board(self) -> None:
        """
        Очистить игровое поле.

        Удаляет все ходы и сбрасывает состояние игры.
        """
        pass

    @abstractmethod
    def switch_player(self) -> None:
        """
        Переключить текущего игрока, если игра активна.

        Обновляет состояние игры, чтобы передать ход другому игроку.
        """
        pass

    @abstractmethod
    def check_game_state(self) -> int:
        """
        Установить статус игры в зависимости от результата хода.

        :return: Статус игры (например, 200 — ожидание, 201 — ход первого игрока, -1 — конец игры).
        """
        pass

class TicTakToeGameService(GameService):
    """Класс, который управляет игровым процессом для игры крестики-нолики"""
    def __init__(self, game_server: GameServer):
        super().__init__(game_server)

    def make_player_move(self, player_id, row_index, col_index):
        """Сделать ход машины."""
        if (self.game_server.status ==  self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE']
                and player_id == self.game_server.current_player1):
            self.game_server.board.game_matrix[row_index][col_index] = self.game_server.PLAYER_ONE_MARKER
            return True
        elif (self.game_server.status == self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE']
              and player_id == self.game_server.current_player2):
            self.game_server.board.game_matrix[row_index][col_index] = self.game_server.PLAYER_TWO_MARKER
            return True

        return False

    def make_machine_move(self):
        """Сделать ход машины с использованием алгоритма минимакс."""
        best_score = float('-inf')
        best_move = None

        for row in range(len(self.game_server.board.game_matrix)):
            for col in range(len(self.game_server.board.game_matrix[row])):
                if self.game_server.board.game_matrix[row][col] == 0:
                    self.game_server.board.game_matrix[row][col] = self.game_server.PLAYER_TWO_MARKER
                    score = self.minimax(0, False)
                    self.game_server.board.game_matrix[row][col] = 0  # Отменяем ход

                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        if best_move:
            row_index, col_index = best_move
            self.game_server.board.game_matrix[row_index][col_index] = self.game_server.PLAYER_TWO_MARKER

    def verify_board(self, row_index, col_index):
        """Проверить, что не изменены предыдущие ходы и можно делать ход"""
        if self.game_server.status not in(self.game_server.GAME_STATE['WAIT PLAYERS'],
                                          self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE'],
                                          self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE']):
            return self.game_server.ERR_CODE['GAME OVER'] # Игра окончена

        if self.game_server.board.game_matrix[row_index][col_index] != 0:
            return self.game_server.ERR_CODE['CELL NOT EMPTY']  # Ход невозможен

        return None

    def check_winner(self):
        """Проверить победителя или ничью."""
        rows = len(self.game_server.board.game_matrix)
        cols = len(self.game_server.board.game_matrix[0])

        # Проверка строк
        for row in range(rows):
            if len(set(self.game_server.board.game_matrix[row])) == 1 and self.game_server.board.game_matrix[row][
                0] != 0:
                return self.game_server.GAME_STATE['CURRENT PLAYER2 WIN'] \
                    if self.game_server.board.game_matrix[row][0] == self.game_server.PLAYER_TWO_MARKER \
                    else self.game_server.GAME_STATE['CURRENT PLAYER1 WIN']

        # Проверка столбцов
        for col in range(cols):
            column_values = [self.game_server.board.game_matrix[row][col] for row in range(rows)]
            if len(set(column_values)) == 1 and column_values[0] != 0:
                return self.game_server.GAME_STATE['CURRENT PLAYER2 WIN'] \
                    if column_values[0] == self.game_server.PLAYER_TWO_MARKER \
                    else self.game_server.GAME_STATE['CURRENT PLAYER1 WIN']

        # Проверка диагоналей
        diagonal_values = [self.game_server.board.game_matrix[row][row] for row in range(rows)]
        if len(set(diagonal_values)) == 1 and diagonal_values[0] != 0:
            return self.game_server.GAME_STATE['CURRENT PLAYER2 WIN'] \
                if diagonal_values[0] == self.game_server.PLAYER_TWO_MARKER \
                else self.game_server.GAME_STATE['CURRENT PLAYER1 WIN']

        diagonal_values = [self.game_server.board.game_matrix[row][cols - row - 1] for row in range(rows)]
        if len(set(diagonal_values)) == 1 and diagonal_values[0] != 0:
            return self.game_server.GAME_STATE['CURRENT PLAYER2 WIN'] \
                if diagonal_values[0] == self.game_server.PLAYER_TWO_MARKER \
                else self.game_server.GAME_STATE['CURRENT PLAYER1 WIN']

        # Ничья
        if all(cell != 0 for row in self.game_server.board.game_matrix for cell in row):
            return self.game_server.GAME_STATE['DRAW']

        # Игра продолжается
        return None

    def clean_board(self):
        self.game_server.board.game_matrix = [[0 for _ in range(len(self.game_server.board.game_matrix[0]))]
                                       for _ in range(len(self.game_server.board.game_matrix))]

    def minimax(self, depth, is_maximizing):
        """Рекурсивный алгоритм минимакс."""
        score = self.check_winner()

        # Если игра завершена, возвращаем оценку
        if score is not None:
            return score

        # Если это ход машины (максимизация)
        if is_maximizing:
            best_score = float('-inf')
            for row in range(len(self.game_server.board.game_matrix)):
                for col in range(len(self.game_server.board.game_matrix[row])):
                    if self.game_server.board.game_matrix[row][col] == 0:
                        self.game_server.board.game_matrix[row][col] = self.game_server.PLAYER_TWO_MARKER
                        score = self.minimax(depth + 1, False)
                        self.game_server.board.game_matrix[row][col] = 0  # Отменяем ход
                        best_score = max(best_score, score)
            return best_score

        # Если это ход игрока (минимизация)
        else:
            best_score = float('inf')
            for row in range(len(self.game_server.board.game_matrix)):
                for col in range(len(self.game_server.board.game_matrix[row])):
                    if self.game_server.board.game_matrix[row][col] == 0:
                        self.game_server.board.game_matrix[row][col] = self.game_server.PLAYER_ONE_MARKER
                        score = self.minimax(depth + 1, True)
                        self.game_server.board.game_matrix[row][col] = 0  # Отменяем ход
                        best_score = min(best_score, score)
            return best_score

    def switch_player(self):
        """Переключить текущего игрока, если игра активна."""
        if self.game_server.status not in (self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE'],
                                          self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE']):
            raise ValueError("Невозможно переключить игрока: игра завершена или не начата")

        self.game_server.status = self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE']\
            if self.game_server.status == self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE'] \
            else self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE']

    def check_game_state(self):
        """Установить статус игры в зависимости от результата хода"""
        if self.game_server.status not in(self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE'],
                                          self.game_server.GAME_STATE['CURRENT PLAYER2 MOVE']):
            return

        game_result = self.check_winner()
        if game_result is None:
            self.switch_player()
        else:
            self.game_server.status = game_result
