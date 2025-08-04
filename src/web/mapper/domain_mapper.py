from domain.model.game_server import GameServer
from domain.service.game_service import TicTakToeGameService
from web.model.game import Game

class DomainMapper:
    GAME_ERROR_MESSAGES = {101: 'Игра окончена, обновите игру', 102: 'Клетка занята, повторите ход'}
    GAME_STATE = {'DRAW': 0, 'CURRENT PLAYER1 WIN': -1, 'CURRENT PLAYER2 WIN': 1, 'WAIT PLAYERS': 200,
                  'CURRENT PLAYER1 MOVE': 201, 'CURRENT PLAYER2 MOVE': 202}

    def __init__(self, game_server: GameServer):
        self.game_server = game_server
        self.game_service = TicTakToeGameService(game_server=self.game_server)
        self.game = Game(uuid=self.game_server.UUID)

    def make_player_move(self, player_id, row_index, col_index):
        """Сделать ход человека."""
        return self.game_service.make_player_move(player_id, row_index, col_index)

    def make_machine_move(self):
        """Сделать ход компьютера."""
        return self.game_service.make_machine_move()

    def verify_board(self, row_index, col_index):
        """Проверить, что не изменены предыдущие ходы"""
        return self.game_service.verify_board(row_index, col_index)

    def make_error_message(self, error_code):
        """Сообщение об ошибке."""
        return self.GAME_ERROR_MESSAGES.get(error_code, None)

    def make_info_message(self) -> str:
        """Сообщение о состоянии игры."""
        match self.game_server.status:
            case 0: return f"Ничья"
            case 1: return f"Победа игрока {self.game_server.current_player2}!" \
                if self.game_server.game_type == 2 else f"Победила машина. Не повезло)"
            case -1: return f"Победа игрока {self.game_server.current_player1}!"
            case 200: return f"Ожидание противника..."
            case 201: return f"Ходит игрок {self.game_server.current_player1}..."
            case 202: return f"Ходит игрок {self.game_server.current_player2}..." \
                if self.game_server.game_type == 2 else f"Ходит машина..."
            case _: return ''

    def switch_player(self):
        """Поменять текущего игрока."""
        return self.game_service.switch_player()

    def check_game_state(self):
        """Проверить состояние игры"""
        return self.game_service.check_game_state()

    def restart_game(self):
        """Обновить игру, очистить игровое поле"""
        self.game_service.clean_board()
        self.game_server.status = self.game_server.GAME_STATE['CURRENT PLAYER1 MOVE']

    @staticmethod
    def convert_index(index):
        """Преобразовать одномерный индекс в двумерный"""
        return index // 3, index % 3


