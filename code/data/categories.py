import sqlalchemy
from .db_session import SqlAlchemyBase


'''post_to_category = sqlalchemy.Table(
    'post_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('post_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('post.id')),
    sqlalchemy.Column('category_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('category.id'))
)'''


class Category(SqlAlchemyBase):
    __tablename__ = "category"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.Integer,
                                 unique=True,
                                 nullable=False)
