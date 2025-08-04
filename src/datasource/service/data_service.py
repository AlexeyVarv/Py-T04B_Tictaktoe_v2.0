class DataService:
    """
    Класс, представляющий сервис данных для управления бизнес-логикой взаимодействия с хранилищем.
    Использует репозиторий для выполнения операций с данными (например, игроками и сохраненными играми).

    Атрибуты:
        repository: Экземпляр репозитория, который предоставляет доступ к данным в хранилище.
    """

    def __init__(self, repository):
        """
        Инициализация сервиса данных.

        :param repository: Экземпляр репозитория (например, GameRepository).
                           Предоставляет интерфейс для работы с данными в хранилище.
        """
        self.repository = repository

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