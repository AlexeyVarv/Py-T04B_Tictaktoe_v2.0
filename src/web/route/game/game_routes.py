from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify, g, session
from dependency_injector.wiring import inject, Provide
from flask_socketio import emit, join_room, rooms
from socketio_init import socketio
import asyncio

from domain.model.game_server import GameServer
from web.model.game import Game
from web.mapper.domain_mapper import DomainMapper
from datasource.service.data_service import DataService
from di.container import Container
from web.authentication.user_authenticator import UserAuthenticator, requires_auth

game_bp = Blueprint('game', __name__, template_folder='templates')
active_games = {}

@game_bp.route('/start-game', methods=['GET'])
@requires_auth(UserAuthenticator(Provide[Container.auth_service]))
@inject
def start_game():
    """Стартовая страница с созданием новой игры."""
    game_type = request.args.get('game_type', default=1, type=int)
    rows = request.args.get('rows', default=3, type=int)
    cols = request.args.get('cols', default=3, type=int)

    user_uuid = session.get('user_uuid')

    # Создание новой игры
    game_server = GameServer(
        rows=rows,
        cols=cols,
        game_type=game_type,
        current_player1=user_uuid,
        status=200 if game_type != 1 else 201
    )
    active_games[game_server.UUID] = game_server

    # Перенаправление на страницу игры
    return redirect(url_for('.game_page', game_id=game_server.UUID))

@game_bp.route('/join-game', methods=['GET'])
@requires_auth(UserAuthenticator(Provide[Container.auth_service]))
def join_game_page():
    """Страница присоединения к игре."""
    current_player_id = session.get('user_uuid')  # Получение ID текущего игрока
    return render_template(
        'game/join_game.html',
        current_player_id=current_player_id
    )

@game_bp.route('/<game_id>', methods=['GET'])
@inject
def game_page(game_id):
    """Страница игрового поля."""
    # Получение игры из активных игр
    game_server = active_games.get(game_id)
    if not game_server:
        return "Игра не найдена", 404
    # ID текущего пользователя
    current_player_id = session.get('user_uuid')
    message = "Ваш значок О" if game_server.current_player1 == current_player_id \
        else "Ваш значок Х"
    # Передача данных в шаблон
    return render_template(
        'game/main_game.html',
        board=game_server.board.game_matrix,  # Текущее состояние доски
        message=message,  # Сообщение (если есть)
        game_id=game_id,  # ID игры
        current_player_id=current_player_id,  # ID текущего игрока
        game_type=game_server.game_type  # Тип игры (1 - игра с машиной, 2 - игра с другим игроком)
    )

@game_bp.route('/load/<uuid>', methods=['GET'])
@inject
def load_game(uuid, service: DataService = Provide[Container.data_service]):
    """Загрузить игру из списка сохраненных."""
    game_server = service.upload_selected_game(uuid)
    if game_server:
        active_games[game_server.UUID] = game_server  # Сохраняем игру в словаре
        return redirect(url_for('.game_page', game_id=game_server.UUID))  # Перенаправление на страницу игры
    return "Игра не найдена", 404

@game_bp.route('/saved-games', methods=['GET'])
@requires_auth(UserAuthenticator(Provide[Container.auth_service]))
@inject
def saved_games(service: DataService = Provide[Container.data_service]):
    """Показать список сохраненных игр для авторизованного пользователя."""
    # Получение UUID пользователя из контекста запроса
    user_uuid = session.get('user_uuid')

    # Получение списка сохраненных игр для данного пользователя
    saved_games_list = service.get_saved_games_by_user(user_uuid)
    return render_template('game/saved_games.html', saved_games=saved_games_list)

@socketio.on('join_game', namespace='/game')
def handle_join_game(data):
    """Обработка подключения игрока к игре."""
    game_id = data['game_id']
    guest_id = data.get('guest')  # ID гостя (может быть None для хозяина)

    # Проверка существования игры
    if game_id not in active_games:
        emit('error', {'message': 'Игра не найдена'})
        return

    join_room(game_id)

    # Создание класса управляющего логикой
    game_server = active_games[game_id]
    domain_mapper = DomainMapper(game_server)

    # Отправка текущего состояния игры
    message = domain_mapper.make_info_message()
    emit('game_process', {'result': message}, room=game_id)

    # Второй игрок (гость)
    if game_server.current_player2 is None and game_server.game_type == 2:
        game_server.current_player2 = guest_id  # Устанавливаем гостя
        if game_server.current_player2:
            game_server.status = 201  # Игра начинается
            emit('game_started', {'message': 'Игра началась!'}, room=game_id)
            return

    # Рассылка обновленного состояния доски всем участникам
    emit('update_board', {'board': game_server.board.game_matrix}, room=game_id)

@socketio.on('make_move', namespace='/game')
def handle_make_move(data):
    """Обработка хода игрока."""
    game_id = data['game_id']
    player_id = data['player_id']
    row, col = data['row'], data['col']

    # Проверка существования игры
    if game_id not in active_games:
        emit('error', {'message': 'Игра не найдена'}, room=game_id)
        return

    # Создание класса управляющего логикой
    game_server = active_games[game_id]
    domain_mapper = DomainMapper(game_server)

    # Проверка корректности хода
    error_code = domain_mapper.verify_board(row, col)  # Переводим координаты в индекс
    if error_code:
        emit('error', {'message': domain_mapper.make_error_message(error_code)}, room=game_id)
        return

    # Ход игрока
    if domain_mapper.make_player_move(player_id, row, col):
        domain_mapper.check_game_state()
        emit('update_board', {'board': game_server.board.game_matrix}, room=game_id)
        # Сообщение о статусе игры
        message = domain_mapper.make_info_message()
        emit('game_process', {'result': message}, room=game_id)

    # Если игра с машиной, выполняем ход машины
    if game_server.game_type == 1 and game_server.status == 202:
        emit('block_input', {}, room=game_id) # Блокировка ввода
        socketio.start_background_task(machine_move_task())
        domain_mapper.make_machine_move()
        domain_mapper.check_game_state()
        emit('update_board', {'board': game_server.board.game_matrix}, room=game_id)
        # Сообщение о статусе игры
        message = domain_mapper.make_info_message()
        emit('game_process', {'result': message}, room=game_id)
        emit('unblock_input', {}, room=game_id)  # Разблокировка ввода

@socketio.on('restart_game', namespace='/game')
def handle_restart_game(data):
    """Начать игру заново."""
    game_id = data['game_id']
    if not game_id:
        emit('error', {'message': 'Игра не найдена'})
        return

    game_server = active_games.get(game_id)
    if not game_server:
        emit('error', {'message': 'Игра не найдена'})
        return
    domain_mapper = DomainMapper(game_server)
    domain_mapper.restart_game()
    message = domain_mapper.make_info_message()
    emit('game_process', {'result': message}, room=game_id)
    emit('update_board', {'board': game_server.board.game_matrix}, room=game_id)

@socketio.on('save_game', namespace='/game')
@inject
def handle_save_game(data, service: DataService = Provide[Container.data_service]):
    """Сохранить игру."""
    # Получаем game_id из формы
    game_id = data['game_id']
    if not game_id:
        emit('error', {'message': 'Игра не найдена'})
        return

    game_server = active_games.get(game_id)
    if not game_server:
        emit('error', {'message': 'Игра не найдена'})
        return

    try:
        service.save_current_game(game_server)
        emit('success', {'message': 'Игра сохранена'})
    except Exception as e:
        emit('error', {'message': f'Ошибка при сохранении игры: {str(e)}'})

def machine_move_task():
    """Асинхронная задача для хода машины."""
    import asyncio
    asyncio.run(async_machine_move())

async def async_machine_move():
    """Логика хода машины с задержкой."""
    await asyncio.sleep(1)  # Задержка 1 секунду
