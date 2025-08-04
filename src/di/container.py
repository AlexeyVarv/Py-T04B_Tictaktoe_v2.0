from dependency_injector import containers, providers
from flask_sqlalchemy import SQLAlchemy
from datasource.repository.game_repository import GameRepository
from datasource.service.data_service import DataService
from web.authentication.auth_service import AuthService
from datasource.model.db_params import define_models


class Container(containers.DeclarativeContainer):
    # Инициализация db
    db = providers.Singleton(SQLAlchemy)

    # Определение моделей
    models = providers.Singleton(define_models, db=db)

    # Репозиторий с зависимостью от db и моделей
    repository = providers.Factory(
        GameRepository,
        db=db,
        players=models.provided[0],
        saved_games=models.provided[2]  # Передаем модель SavedGames
    )

    # Сервис с зависимостью от репозитория
    data_service = providers.Factory(
        DataService,
        repository=repository
    )

    # Сервис авторизации
    auth_service = providers.Factory(
        AuthService,
        user_service=data_service
    )
