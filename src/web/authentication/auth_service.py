from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64decode
from pydantic import BaseModel, validator

class SignUpRequest(BaseModel):
    login: str
    password: str
    confirm_password: str

    @validator('login')
    def validate_login(cls, value):
        if len(value) < 3:
            raise ValueError('Логин должен содержать минимум 3 символа')
        return value

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return value

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

class AuthService:
    def __init__(self, user_service):
        self.user_service = user_service

    def register(self, sign_up_request: SignUpRequest) -> bool:
        """
        Регистрация пользователя.
        :param sign_up_request: Данные для регистрации (логин и пароль).
        :return: True, если регистрация успешна, иначе False.
        """
        if sign_up_request.password != sign_up_request.confirm_password:
            raise ValueError("The passwords do not match")
        if self.user_service.get_user(sign_up_request.login):
            return False  # Пользователь уже существует
        hashed_password = generate_password_hash(sign_up_request.password)
        self.user_service.save_user(login=sign_up_request.login, password=hashed_password)
        return True

    def authenticate(self, auth_header: str) -> str:
        """
        Авторизация пользователя.
        :param auth_header: Заголовок Authorization в формате "Basic base64(login:password)".
        :return: UUID пользователя, если авторизация успешна.
        :raises ValueError: Если авторизация не удалась.
        """
        if not auth_header or not auth_header.startswith("Basic "):
            raise ValueError("Invalid authorization header")

        # Декодирование логина и пароля
        try:
            credentials = b64decode(auth_header.split(" ")[1]).decode("utf-8")
            login, password = credentials.split(":")
        except Exception:
            raise ValueError("Invalid credentials format")

        # Поиск пользователя
        user = self.user_service.get_user(login)
        if not user or not check_password_hash(user.password, password):
            raise ValueError("Invalid login or password")

        return user.uuid
