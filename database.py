from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import Session, declared_attr, declarative_base

import datetime


engine = create_engine("sqlite:///autocomplete.db", echo=True)
session = Session(engine)


class PreBase:
    @declared_attr
    def __tablename__(cls):
        # В моделях-наследниках свойство __tablename__ будет создано
        # из имени модели, переведённого в нижний регистр.
        # Возвращаем это значение.
        return cls.__name__.lower()

    # В моделях-наследниках будет создана колонка id типа Integer
    id = Column(Integer, primary_key=True)


# Декларативная база включит в себя атрибуты,
# описанные в классе PreBase.
Base = declarative_base(cls=PreBase)


# Наследники класса Base теперь автоматически получат
# приватный атрибут __tablename__ и атрибут id.
# Описываем модель:
class User(Base):
    first_name = Column(String)
    last_name = Column(String(200))
    email = Column(String(200))
    phone = Column(Integer)
    date = Column(Date)

    def __str__(self):
        # При вызове функции print()
        # будут выводиться значения полей first_name и last_name.
        return f"User {self.first_name} {self.last_name}"


Base.metadata.create_all(engine)


def adding_data_database(**kwargs):
    """функция добавляет данные в базу данных"""
    fields_name = {}
    for field, value in kwargs.items():
        fields_name[field] = value

    user = User(
        first_name=fields_name["first_name"],
        last_name=fields_name["last_name"],
        email=fields_name["email"],
        phone=fields_name["phone"],
        date=datetime.datetime.strptime(fields_name["date"], "%d.%m.%Y"),
    )

    session.add(user)
    session.commit()
