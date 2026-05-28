"""Модуль для создания Flask-приложения."""
import os
from flask import Flask, redirect, url_for, send_from_directory

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """Создание и настройка Flask-приложения."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'obuv-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.orders_purchase import purchase_bp

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(purchase_bp)

    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        # Раздаём загруженные изображения из папки UPLOAD_FOLDER (uploads/)
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        return send_from_directory(upload_dir, filename)



    
    with app.app_context():
        db.create_all()
    
    return app