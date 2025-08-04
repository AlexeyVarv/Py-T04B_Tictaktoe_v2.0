from datasource.mapper.game_data_mapper import GameDataMapper


class GameRepository:
    def __init__(self, db, players, saved_games):
        self.db = db
        self.players = players
        self.saved_games = saved_games

    def save_game_to_db(self, game_server):
        """Сохранить текущую игру в БД."""
        try:
            # Проверка, существует ли игра с указанным UUID
            game_form_db = self.get_saved_game_by_uuid(game_server.UUID)

            if game_form_db is None:
                game_db = GameDataMapper.game_to_database(game_server, self.saved_games)
                self.db.session.add(game_db)  # Добавление новой записи в сессию
            else:
                self.delete_game(game_form_db.UUID) # Удаляем старую игру и сохраняем заново
                game_db = GameDataMapper.game_to_database(game_server, self.saved_games)
                self.db.session.add(game_db)
            self.db.session.commit()
        except Exception as e:
            # Откат транзакции в случае ошибки
            self.db.session.rollback()
            raise ValueError(f"Ошибка при сохранении игры: {str(e)}")

    def get_saved_game_by_uuid(self, game_uuid):
        """Получить игру по uuid."""
        try:
            return GameDataMapper.game_from_database(self.db, game_uuid, self.saved_games)
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_all_games(self):
        """Получить список всех игр."""
        try:
            games = self.db.session.execute(self.db.select(self.saved_games)).scalars().all()
            return [GameDataMapper.game_from_database(self.db, game.uuid, self.saved_games) for game in games]
        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete_game(self, game_uuid):
        """Удалить игру по uuid."""
        print("Start delete...")
        try:
            game = self.db.session.execute(
                self.db.select(self.saved_games).filter_by(game_uuid=game_uuid)
            ).scalar_one_or_none()
            if game:
                self.db.session.delete(game)
                self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def save_user(self, login, password):
        """Сохранить пользователя в БД."""
        try:
            user_db = self.players(login=login, password=password)
            self.db.session.add(user_db)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_user(self, login):
        """Получить пользователя из БД."""
        try:
            return self.db.session.execute(
                self.db.select(self.players).filter_by(login=login)
            ).scalar_one_or_none()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_user_by_uuid(self, user_uuid):
        """Получить пользователя из БД."""
        try:
            return self.db.session.execute(
                self.db.select(self.players).filter_by(uuid=user_uuid)
            ).scalar_one_or_none()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_saved_games_by_user(self, user_uuid):
        """Получить список сохраненных игр для пользователя."""
        try:
            # if isinstance(user_uuid, str):
            #     user_uuid = uuid.UUID(user_uuid)

            return self.db.session.execute(
                self.db.select(self.saved_games).filter_by(player_owner_uuid=user_uuid)
                .union(
                    self.db.select(self.saved_games).filter_by(player_guest_uuid=user_uuid)
                )
            ).all()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_user_id_by_uuid(self, user_uuid):
        """Получить ID пользователя из БД по UUID."""
        try:
            result = self.db.session.execute(
                self.db.select(self.players.id).filter_by(uuid=user_uuid)
            ).scalar_one_or_none()
            if result is None:
                raise ValueError("Пользователь с указанным UUID не найден")
            return result
        except Exception as e:
            self.db.session.rollback()
            raise ValueError("Произошла ошибка при получении ID пользователя") from e
