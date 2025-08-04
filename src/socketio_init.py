# socketio_init.py
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def init_socketio(app: Flask):
    """Инициализация Socket.IO."""
    socketio.init_app(app, cors_allowed_origins="*")
