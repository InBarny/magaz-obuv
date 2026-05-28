"""Скрипт для инициализации базы данных и создания тестовых данных."""
from app import create_app, db
from app.models import User, Category, Manufacturer, Supplier, Product, Order, OrderItem


def init_db():
    """Инициализация базы данных с тестовыми данными."""
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        users = [
            User(login='admin', role='admin', fio='Администратор Системы'),
            User(login='manager', role='manager', fio='Менеджер Магазина'),
            User(login='client', role='client', fio='Клиент Покупатель'),
            User(login='guest', role='guest', fio='Гость'),
        ]
        
        for user in users:
            user.set_password('12345')
            db.session.add(user)
        
        categories = [
            Category(name='Кроссовки'),
            Category(name='Ботинки'),
            Category(name='Сандалии'),
            Category(name='Сапоги'),
            Category(name='Тапочки'),
        ]
        for cat in categories:
            db.session.add(cat)
        
        manufacturers = [
            Manufacturer(name='Nike'),
            Manufacturer(name='Adidas'),
            Manufacturer(name='Puma'),
            Manufacturer(name='Reebok'),
            Manufacturer(name='New Balance'),
        ]
        for man in manufacturers:
            db.session.add(man)
        
        suppliers = [
            Supplier(name='ООО "ОбувьТрейд"'),
            Supplier(name='ИП Сидоров'),
            Supplier(name='ЗАО "СпортСнаб"'),
        ]
        for sup in suppliers:
            db.session.add(sup)
        
        db.session.commit()
        
        products = [
            Product(name='Кроссовки Nike Air Max', category_id=1, description='Легкие и комфортные кроссовки для бега',
                   manufacturer_id=1, supplier_id=1, price=8999, unit='пара', stock=15, discount=10, image_path='uploads/1.jpg'),
            Product(name='Ботинки Adidas Terrex', category_id=2, description='Водонепроницаемые ботинки для походов',
                   manufacturer_id=2, supplier_id=3, price=12999, unit='пара', stock=8, discount=0, image_path='uploads/2.jpg'),
            Product(name='Сандалии Puma Dower', category_id=3, description='Летние сандалии для активного отдыха',
                   manufacturer_id=3, supplier_id=2, price=3499, unit='пара', stock=20, discount=0, image_path='uploads/3.jpg'),
            Product(name='Сапоги Reebok Stomper', category_id=4, description='Зимние сапоги с утеплителем',
                   manufacturer_id=4, supplier_id=1, price=7999, unit='пара', stock=0, discount=20, image_path='uploads/4.jpg'),
            Product(name='Кроссовки New Balance 574', category_id=1, description='Классические кроссовки на каждый день',
                   manufacturer_id=5, supplier_id=2, price=6499, unit='пара', stock=12, discount=0, image_path='uploads/5.jpg'),
            Product(name='Ботинки Nike SB', category_id=2, description='Ботинки для скейтбординга',
                   manufacturer_id=1, supplier_id=3, price=5499, unit='пара', stock=5, discount=0, image_path='uploads/6.jpg'),
            Product(name='Тапочки Puma House', category_id=5, description='Домашние тапочки',
                   manufacturer_id=3, supplier_id=1, price=999, unit='пара', stock=50, discount=0, image_path='uploads/7.jpg'),
            Product(name='Кроссовки Adidas Ultraboost', category_id=1, description='Беговые кроссовки премиум-класса',
                   manufacturer_id=2, supplier_id=2, price=15999, unit='пара', stock=3, discount=0, image_path='uploads/8.jpg'),
        ]
        for prod in products:
            db.session.add(prod)
        
        db.session.commit()
        
        print("База данных успешно инициализирована!")
        print("\nТестовые аккаунты:")
        print("  Логин: admin    | Пароль: 12345 | Роль: Администратор")
        print("  Логин: manager  | Пароль: 12345 | Роль: Менеджер")
        print("  Логин: client   | Пароль: 12345 | Роль: Клиент")
        print("  Логин: guest    | Пароль: 12345 | Роль: Гость")


if __name__ == '__main__':
    init_db()