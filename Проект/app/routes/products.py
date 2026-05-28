"""Маршруты для работы с товарами."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from app import db
from app.models import Product, Category, Manufacturer, Supplier

products_bp = Blueprint('products', __name__, url_prefix='/products')


def allowed_file(filename):
    """Проверка расширения файла."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@products_bp.route('/')
def product_list():
    """Список товаров."""
    query = Product.query
    
    search = request.args.get('search', '')
    supplier_filter = request.args.get('supplier', '')
    sort_order = request.args.get('sort', '')
    sort_direction = request.args.get('direction', 'asc')
    
    if search and current_user.is_authenticated and current_user.has_permission('search_products'):
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                Product.name.ilike(search_filter),
                Product.description.ilike(search_filter),
                Category.name.ilike(search_filter),
                Manufacturer.name.ilike(search_filter)
            )
        )
    
    if supplier_filter and current_user.is_authenticated and current_user.has_permission('filter_products'):
        query = query.filter(Product.supplier_id == int(supplier_filter))
    
    if sort_order and current_user.is_authenticated and current_user.has_permission('sort_products'):
        if sort_order == 'stock':
            if sort_direction == 'desc':
                query = query.order_by(Product.stock.desc())
            else:
                query = query.order_by(Product.stock.asc())
    
    products = query.join(Category).join(Manufacturer).join(Supplier).all()
    categories = Category.query.all()
    manufacturers = Manufacturer.query.all()
    suppliers = Supplier.query.all()
    
    return render_template(
        'products.html',
        products=products,
        categories=categories,
        manufacturers=manufacturers,
        suppliers=suppliers,
        search=search,
        selected_supplier=supplier_filter,
        sort_order=sort_order,
        sort_direction=sort_direction
    )


@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Добавление товара (только админ)."""
    if not current_user.has_permission('add_product'):
        flash('У вас нет прав для добавления товара', 'error')
        return redirect(url_for('products.product_list'))
    
    categories = Category.query.all()
    manufacturers = Manufacturer.query.all()
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        try:
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    img = Image.open(file)
                    img = img.resize((300, 200), Image.Resampling.LANCZOS)
                    img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            product = Product(
                name=request.form.get('name'),
                category_id=int(request.form.get('category_id')),
                description=request.form.get('description'),
                manufacturer_id=int(request.form.get('manufacturer_id')),
                supplier_id=int(request.form.get('supplier_id')),
                price=float(request.form.get('price')),
                unit=request.form.get('unit'),
                stock=int(request.form.get('stock')),
                discount=int(request.form.get('discount', 0)),
                image_path=image_path
            )
            
            if product.price < 0 or product.stock < 0:
                flash('Цена и количество не могут быть отрицательными', 'error')
                return redirect(url_for('products.add_product'))
            
            db.session.add(product)
            db.session.commit()
            flash('Товар успешно добавлен', 'success')
            return redirect(url_for('products.product_list'))
        except Exception as e:
            flash(f'Ошибка при добавлении товара: {str(e)}', 'error')
    
    return render_template('product_form.html', 
                           categories=categories,
                           manufacturers=manufacturers,
                           suppliers=suppliers,
                           product=None,
                           title='Добавление товара')


@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Редактирование товара (только админ)."""
    if not current_user.has_permission('edit_product'):
        flash('У вас нет прав для редактирования товара', 'error')
        return redirect(url_for('products.product_list'))
    
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    manufacturers = Manufacturer.query.all()
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    if product.image_path and os.path.exists(product.image_path):
                        os.remove(product.image_path)
                    
                    filename = secure_filename(file.filename)
                    img = Image.open(file)
                    img = img.resize((300, 200), Image.Resampling.LANCZOS)
                    img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    product.image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            product.name = request.form.get('name')
            product.category_id = int(request.form.get('category_id'))
            product.description = request.form.get('description')
            product.manufacturer_id = int(request.form.get('manufacturer_id'))
            product.supplier_id = int(request.form.get('supplier_id'))
            product.price = float(request.form.get('price'))
            product.unit = request.form.get('unit')
            product.stock = int(request.form.get('stock'))
            product.discount = int(request.form.get('discount', 0))
            
            if product.price < 0 or product.stock < 0:
                flash('Цена и количество не могут быть отрицательными', 'error')
                return redirect(url_for('products.edit_product', product_id=product_id))
            
            db.session.commit()
            flash('Товар успешно обновлён', 'success')
            return redirect(url_for('products.product_list'))
        except Exception as e:
            flash(f'Ошибка при обновлении товара: {str(e)}', 'error')
    
    return render_template('product_form.html',
                           categories=categories,
                           manufacturers=manufacturers,
                           suppliers=suppliers,
                           product=product,
                           title='Редактирование товара')


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Удаление товара (только админ)."""
    if not current_user.has_permission('delete_product'):
        flash('У вас нет прав для удаления товара', 'error')
        return redirect(url_for('products.product_list'))
    
    product = Product.query.get_or_404(product_id)
    
    if product.order_items:
        flash('Невозможно удалить товар, он присутствует в заказе', 'error')
        return redirect(url_for('products.product_list'))
    
    try:
        if product.image_path and os.path.exists(product.image_path):
            os.remove(product.image_path)
        
        db.session.delete(product)
        db.session.commit()
        flash('Товар успешно удалён', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении товара: {str(e)}', 'error')
    
    return redirect(url_for('products.product_list'))