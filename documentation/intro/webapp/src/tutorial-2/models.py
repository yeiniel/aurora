
import sqlalchemy
from sqlalchemy.ext import declarative

__all__ = ['Post']


Model = declarative.declarative_base()


class Post(Model):
    __tablename__ = 'blog_post'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)