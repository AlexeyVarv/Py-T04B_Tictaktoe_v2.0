class DataService:
    def __init__(self, repository):
        self.repository = repository  # Репозиторий для работы с хранилищем

    def save_current_game(self, game_server):
        """Сохранить текущую игру."""
        return self.repository.save_game_to_db(game_server)

    def upload_selected_game(self, game_uuid):
        """Загрузить выбранную игру."""
        return self.repository.get_saved_game_by_uuid(game_uuid)

    def get_all_saved_games(self):
        """Получить список всех сохраненных игр."""
        return self.repository.get_all_games()

    def get_saved_games_by_user(self, user_uuid):
        """Получить список всех сохраненных игр конкретного игрока."""
        return self.repository.get_saved_games_by_user(user_uuid)

    def delete_game(self, game_uuid):
        """Удалить сохраненную игру."""
        self.repository.delete_game(game_uuid)

    def save_user(self, login, password):
        """Сохранить игрока в БД."""
        print("save_user")
        return self.repository.save_user(login, password)

    def get_user(self, login):
        """Получить игрока из БД."""
        return self.repository.get_user(login)

    def get_user_by_uuid(self, user_uuid):
        """Получить игрока из БД."""
        return self.repository.get_user_by_uuid(user_uuid)

    def get_user_id_by_uuid(self, user_uuid):
        """Получить игрока из БД."""
        return self.repository.get_user_id_by_uuid(user_uuid)