from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

DATABASE_URL = "postgresql://fitstreet:Stdvan1x@localhost/product_items"
# "postgresql://username:password@host/db_name"

engine = create_engine(DATABASE_URL) # соединение с бд
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # способ обращения к бд

Base = declarative_base() # Хранится настройка для каждой таблицы

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)

Base.metadata.create_all(bind=engine)

ItemPydentic = sqlalchemy_to_pydantic(Item, exclude=['id']) # валидация данных перед отправкой в бд

#API - посмотреть что это.

db_item = ItemPydentic(name = 'Iphone 15', description = 'Iphone 15 1 TB blue', price = 5000)
db_update_item = ItemPydentic(name = 'Nokia', description = '3310', price = 545)
def create_item(db_item: ItemPydentic):
    """
    добавляет новый элемент в таблицу
    """    
    with SessionLocal() as db:
        db_item = Item(**db_item.dict())
        db.add(db_item)# под капотом insert into
        db.commit() # подтверждаем изменения
        db.refresh(db_item) # обновляем сессию(очищаем сессию)
    return db_item


def get_item():
    """
    получение всех элементов из таблицы
    """
    result = []
    with SessionLocal() as db:
        items = db.query(Item).all()
        for item in items:
            result.append({'name':item.name,
            'description':item.description,
            'price': item.price})
    return result

def retrieve_item(item_id:int):
    """
    получение информации о конкретном продукте по ID
    """
    with SessionLocal() as db:
        retrieved_item = db.query(Item).get(item_id) # filter_by(id=item_id).first()

    if retrieved_item:
        return {
            'name': retrieved_item.name,
            'description': retrieved_item.description,
            'price': retrieved_item.price
               }
    else:
        return f"Продукта с id {item_id} не найдено"

def update_item(item_id:int,name: str, description: str, price:int):
    """
    обновление продукта по ID
    """
    with SessionLocal() as db:
        item_to_update = db.query(Item).get(item_id)
        if item_to_update:
            item_to_update.name = name
            item_to_update.description = description
            item_to_update.price = price
            db.commit()
            db.refresh(item_to_update)
            return {
                'name': item_to_update.name,
                'description': item_to_update.description,
                'price': item_to_update.price
                   }
        else:
            return f"Продукта с {item_id} ID не найдено, обновление не выполнено"
        
def delete_item(item_id: int):
    """
    Удаление продукта по ID.
    """
    with SessionLocal() as db:
        item_to_delete = db.query(Item).get(item_id)
        if item_to_delete:
            db.delete(item_to_delete)
            db.commit()
            return f"Продукт с ID {item_id} успешно удален"
        else:
            return f"Продукта с {item_id} ID не найдено, удаление не выполнено"


#print(update_item(1, "Nokia", "3310", 500 ))
# print(retrieve_item())
# create_item(db_item)





