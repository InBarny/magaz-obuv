"""Маршруты авторизации."""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""
    if current_user.is_authenticated:
        return redirect(url_for('products.product_list'))
    
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(login=login_input).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('products.product_list'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('password')
        fio = request.form.get('fio')
        
        if User.query.filter_by(login=login_input).first():
            flash('Такой логин уже существует', 'error')
            return redirect(url_for('auth.register'))
        
        user = User(login=login_input, role='client', fio=fio)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация прошла успешно! Войдите в систему.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')