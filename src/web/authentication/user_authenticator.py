from functools import wraps
from flask import redirect, url_for, request, jsonify, g, Response, session


class UserAuthenticator:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def authenticate_request(self):
        """
        Проверяет авторизацию запроса.
        :return: UUID пользователя, если авторизация успешна.
        :raises ValueError: Если авторизация не удалась.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # Перенаправление на страницу входа с параметром next
            return redirect(url_for('auth.login', next=request.url, error='Пожалуйста, авторизуйтесь'))

        try:
            user_uuid = self.auth_service.authenticate(auth_header)
            return user_uuid
        except ValueError as e:
            raise ValueError(str(e))

def requires_auth(authenticator):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Проверяем, есть ли UUID пользователя в сессии
            user_uuid = session.get('user_uuid')
            if not user_uuid:
                result = authenticator.authenticate_request()
                if isinstance(result, Response) and result.status_code == 302:
                    return result
                user_uuid = result
                session['user_uuid'] = str(user_uuid)  # Сохраняем UUID в сессии

            g.user_uuid = user_uuid
            return f(*args, **kwargs)
        return decorated_function
    return decorator
