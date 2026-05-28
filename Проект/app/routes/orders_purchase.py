"""Дополнительные маршруты для оформления покупки."""

from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import Product, Order, OrderItem


purchase_bp = Blueprint('purchase', __name__, url_prefix='/purchase')


@purchase_bp.route('/buy/<int:product_id>', methods=['POST'])
@login_required
def buy_product(product_id: int):
    """Оформление покупки 1 товара (без корзины)."""

    if not current_user.has_permission('place_order'):
        flash('У вас нет прав для оформления заказа', 'error')
        return redirect(url_for('products.product_list'))

    product = Product.query.get_or_404(product_id)

    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity < 1:
        quantity = 1

    if product.stock < quantity:
        flash('Недостаточно товара на складе', 'error')
        return redirect(url_for('products.product_list'))

    total_price = round(product.final_price * quantity, 2)

    order = Order(user_id=current_user.id, total_price=total_price, status='новый')
    order_item = OrderItem(
        order=order,
        product_id=product.id,
        quantity=quantity,
        price=product.final_price,
    )

    product.stock -= quantity

    db.session.add(order)
    db.session.add(order_item)
    db.session.commit()

    flash(f'Заказ оформлен. ID заказа: {order.id}', 'success')
    return redirect(url_for('orders.order_detail', order_id=order.id))

