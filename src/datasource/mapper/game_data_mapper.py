import json
from domain.model.game_server import GameServer


class GameDataMapper:
    @staticmethod
    def game_from_database(db, game_uuid, saved_games):
        """Возвращает игру из БД по uuid и переводит в формат модели бизнес-логики"""
        game_data = db.session.execute(db.select(saved_games).filter_by(game_uuid=game_uuid)).scalar_one_or_none()
        if not game_data:
            return None

            # Преобразуем строковое представление доски в матрицу
        board_matrix = json.loads(game_data.board)  # Десериализация JSON
        # Создаем объект GameServer
        game_server = GameServer(
            rows=len(board_matrix),
            cols=len(board_matrix[0]),
            game_uuid=str(game_data.game_uuid),
            game_type=game_data.game_type,
            current_player1=str(game_data.player_owner_uuid),
            current_player2=str(game_data.player_guest_uuid),
            status=int(game_data.game_status),
        )

        # Устанавливаем дополнительные атрибуты
        game_server.board.game_matrix = board_matrix

        return game_server


    @staticmethod
    def game_to_database(game_server, saved_games):
        """Сохранят текущую игру из БД, переводит формат модели бизнес-логики в формат БД"""
        board_json = json.dumps(game_server.board.game_matrix) # Сериализация JSON

        return saved_games(
            game_uuid=game_server.UUID,
            board=board_json,
            player_owner_uuid=game_server.current_player1,
            player_guest_uuid=game_server.current_player2,
            game_status=game_server.status if game_server.status is not None else None,
            game_type=game_server.game_type,
        )

    @staticmethod
    def update_game_in_database(game_server, saved_games):
        """Обновляет существующую запись игры в формате БД."""
        print("Starting update...")
        board_json = json.dumps(game_server.board.game_matrix)

        # Обновление полей записи
        saved_games.board = board_json
        saved_games.player_owner_uuid = game_server.current_player1
        saved_games.player_guest_uuid = game_server.current_player2
        saved_games.game_status = game_server.status if game_server.status is not None else None
        saved_games.game_type = game_server.game_type

        return saved_games  # Возвращаем обновленный объект (опционально)

