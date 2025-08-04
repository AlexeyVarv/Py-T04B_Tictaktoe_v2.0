from flask import Flask, render_template, redirect, url_for, session
from socketio_init import socketio, init_socketio
from dependency_injector.wiring import inject, Provide
from di.container import Container

from web.route.game.game_routes import game_bp
from web.route.auth.auth_routes import auth_bp

# Создание приложения Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://school21:12345@localhost/games'
app.config['SECRET_KEY'] = 'sarfh7575a15adahduf58kgfh'

# Инициализация DI-контейнера
container = Container()
# Получение экземпляра db из контейнера
db = container.db()
# Привязка db к приложению Flask
db.init_app(app)

# Создание таблиц в базе данных
Players, Profiles, SavedGames = container.models()
with app.app_context():
    db.create_all()

init_socketio(app)

# Регистрация blueprint'ов
app.register_blueprint(game_bp, url_prefix='/game')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Использование DI-контейнера
container.wire(modules=[__name__, "web.route.game.game_routes", "web.route.auth.auth_routes"])

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

