"""Маршруты для работы с заказами."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Product, User

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


def _can_view_order(order):
    """Проверка прав на просмотр конкретного заказа."""
    if current_user.role == 'admin' or current_user.role == 'manager':
        return True
    if current_user.role == 'client' and order.user_id == current_user.id:
        return True
    return False


@orders_bp.route('/')
@login_required
def order_list():
    """Список заказов."""
    if current_user.role == 'guest':
        flash('Для просмотра заказов необходимо авторизоваться', 'warning')
        return redirect(url_for('auth.login'))

    if current_user.has_permission('view_orders'):
        orders = Order.query.order_by(Order.created_at.desc()).all()
    elif current_user.has_permission('view_own_orders'):
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    else:
        flash('У вас нет прав для просмотра заказов', 'error')
        return redirect(url_for('products.product_list'))

    return render_template('orders.html', orders=orders)


@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """Детали заказа."""
    order = Order.query.get_or_404(order_id)

    if not _can_view_order(order):
        flash('У вас нет прав для просмотра этого заказа', 'error')
        return redirect(url_for('orders.order_list'))

    return render_template('order_detail.html', order=order)


@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    """Добавление заказа (только администратор)."""
    if not current_user.has_permission('add_order'):
        flash('У вас нет прав для добавления заказа', 'error')
        return redirect(url_for('orders.order_list'))

    users = User.query.filter(User.role != 'guest').all()
    products = Product.query.all()

    if request.method == 'POST':
        try:
            user_id = int(request.form.get('user_id'))
            status = request.form.get('status', 'новый')
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')

            order = Order(user_id=user_id, status=status, total_price=0)
            db.session.add(order)
            db.session.flush()  # Получаем order.id

            total = 0
            for pid, qty in zip(product_ids, quantities):
                if not pid:
                    continue
                product = Product.query.get(int(pid))
                quantity = int(qty)
                if product and quantity > 0:
                    price = product.final_price
                    line_total = round(price * quantity, 2)
                    item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity,
                        price=price
                    )
                    db.session.add(item)
                    total += line_total

            order.total_price = round(total, 2)
            db.session.commit()
            flash('Заказ успешно добавлен', 'success')
            return redirect(url_for('orders.order_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении заказа: {str(e)}', 'error')

    return render_template('order_form.html', order=None, users=users, products=products, title='Добавление заказа')


@orders_bp.route('/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Редактирование заказа (только администратор)."""
    if not current_user.has_permission('edit_order'):
        flash('У вас нет прав для редактирования заказа', 'error')
        return redirect(url_for('orders.order_list'))

    order = Order.query.get_or_404(order_id)
    users = User.query.filter(User.role != 'guest').all()
    products = Product.query.all()

    if request.method == 'POST':
        try:
            order.user_id = int(request.form.get('user_id'))
            order.status = request.form.get('status', 'новый')

            # Удаляем старые позиции и пересоздаём
            OrderItem.query.filter_by(order_id=order.id).delete()

            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')

            total = 0
            for pid, qty in zip(product_ids, quantities):
                if not pid:
                    continue
                product = Product.query.get(int(pid))
                quantity = int(qty)
                if product and quantity > 0:
                    price = product.final_price
                    line_total = round(price * quantity, 2)
                    item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity,
                        price=price
                    )
                    db.session.add(item)
                    total += line_total

            order.total_price = round(total, 2)
            db.session.commit()
            flash('Заказ успешно обновлён', 'success')
            return redirect(url_for('orders.order_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении заказа: {str(e)}', 'error')

    return render_template('order_form.html', order=order, users=users, products=products, title='Редактирование заказа')


@orders_bp.route('/delete/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """Удаление заказа (только администратор)."""
    if not current_user.has_permission('delete_order'):
        flash('У вас нет прав для удаления заказа', 'error')
        return redirect(url_for('orders.order_list'))

    order = Order.query.get_or_404(order_id)
    try:
        db.session.delete(order)
        db.session.commit()
        flash('Заказ успешно удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении заказа: {str(e)}', 'error')

    return redirect(url_for('orders.order_list'))
