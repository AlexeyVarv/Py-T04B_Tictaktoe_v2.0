from flask import Blueprint, request, redirect, url_for, render_template, jsonify, g, session
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from datasource.service.data_service import DataService
from dependency_injector.wiring import inject, Provide
from di.container import Container
from web.authentication.auth_service import AuthService, SignUpRequest
from web.authentication.user_authenticator import UserAuthenticator, requires_auth


auth_bp = Blueprint('auth', __name__, template_folder='templates')

def generate_csrf_token(secret_key, user_id=None):
    """
    Генерация CSRF-токена.
    :param secret_key: Секретный ключ приложения.
    :param user_id: Идентификатор пользователя (опционально).
    :return: CSRF-токен.
    """
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(user_id or 'default')

def validate_csrf_token(token, secret_key, max_age=3600):
    """
    Проверка CSRF-токена.
    :param token: CSRF-токен.
    :param secret_key: Секретный ключ приложения.
    :param max_age: Время жизни токена в секундах.
    :return: True, если токен действителен, иначе False.
    """
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        serializer.loads(token, max_age=max_age)
        return True
    except:
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
@inject
def login(auth_service: AuthService = Provide[Container.auth_service]):
    """
    Обработчик авторизации пользователя через AJAX.
    """
    if request.method == 'POST':
        try:
            # Получение заголовка Authorization
            auth_header = request.headers.get('Authorization')

            # Авторизация через AuthService
            user_uuid = auth_service.authenticate(auth_header)
            session['user_uuid'] = str(user_uuid)
            next_url = request.args.get('next')  # Получение параметра next

            # Перенаправление на нужный ресурс после успешной авторизации
            # return redirect(next_url or url_for('home'))  # Переход на главную страницу по умолчанию
            return jsonify({'redirect_url': next_url}), 200
            # return jsonify({'message': 'Login successful', 'user_uuid': user_uuid}), 200
        except ValueError:
            # Возврат формы с сообщением об ошибке
            return jsonify({'error': 'Неверный логин или пароль'}), 401
        except Exception as e:
            return jsonify({'error': f'Internal server error, {e}'}), 500
    else:
        error_message = request.args.get('error')
        success_message = request.args.get('message')
        return render_template('auth/login.html', next=request.url,
                               error=error_message if error_message else "",
                               message=success_message if success_message else "")

@auth_bp.route('/register', methods=['GET', 'POST'])
@inject
def register(auth_service: AuthService = Provide[Container.auth_service]):
    """
    Обработчик регистрации пользователя через AJAX.
    """
    if request.method == 'POST':
        # Проверка CSRF-токена
        csrf_token = request.headers.get('X-CSRF-Token')
        if not validate_csrf_token(csrf_token, current_app.config['SECRET_KEY']):
            return jsonify({'error': 'Неверный CSRF-токен'}), 403

        try:
            # Получение данных из JSON
            data = request.get_json()
            user_login = data.get('login')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not user_login or not password:
                return jsonify({'error': 'Логин и пароль обязательны'}), 400

            # Создание объекта SignUpRequest
            sign_up_request = SignUpRequest(login=user_login, password=password, confirm_password=confirm_password)

            # Попытка регистрации через AuthService
            success = auth_service.register(sign_up_request)
            if success:
                return jsonify({
                    'redirect_url': url_for('auth.login', message=f'Пользователь {user_login} зарегистрирован! Пожалуйста, войдите.')
                }), 201
            else:
                return jsonify({'error': f'Пользователь {user_login} уже зарегистрирован!'}), 409

        except Exception as e:
            # Обработка ошибок валидации
            if hasattr(e, 'errors') and callable(e.errors):
                errors = e.errors()
                error_messages = [error['msg'].split(',')[1] for error in errors]
                return jsonify({'error': ', '.join(error_messages)}), 400
            else:
                # Для других типов ошибок
                return jsonify({'error': str(e)}), 500
    else:
        return render_template('auth/register.html', error=None)

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """Выход из системы."""
    session.pop('user_uuid', None)  # Удаляем UUID пользователя из сессии
    return redirect(url_for('home'))

@auth_bp.route('/profile/<user_uuid>', methods=['GET'])
def view_profile(user_uuid):
    """Страница профиля пользователя."""
    # Проверяем, что пользователь авторизован и UUID совпадает
    if session.get('user_uuid') != user_uuid:
        return redirect(url_for('auth.login', next=request.url))

    # Логика получения данных профиля
    return render_template('auth/profile.html', current_user=user_uuid, error=None)

@auth_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    Получение CSRF-токена.
    """
    token = generate_csrf_token(current_app.config['SECRET_KEY'])
    return jsonify({'csrf_token': token}), 200
