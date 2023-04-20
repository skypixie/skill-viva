import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Таблица постов пользователей
# Поля: id, user_id, published, heading, content
class Post(SqlAlchemyBase):
    __tablename__ = 'post'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    
    user = orm.relationship('User')
    
    published = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    heading = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey('category.id'))
