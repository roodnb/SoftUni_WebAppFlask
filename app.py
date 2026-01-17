from flask import Flask, request # Flask e class, koito idva ot modula flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import  Resource, Api
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from flask_migrate import Migrate


app = Flask(__name__) # tova ni e nachalaoto na samiq flask app
# app.config['SQLALCHEMY_DATABASE_URI'] =
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)
api = Api(app)
migrate = Migrate(app, db)



class BookModel(db.Model):
    __tablename__ = 'books'
    # the below table construction is how it will look like in SQLAlchemy V2
    # book_id = db.Column(db.Integer, primary_key=True)
    # book_title = db.Column(db.String, primary_key=False)
    # book_author = db.Column(db.String, primary_key=False)

    book_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_title: Mapped[str] = mapped_column(String(100), nullable=False)
    book_author: Mapped[str] = mapped_column(String(50), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey('readers.id'), nullable=True)

    reader: Mapped['ReaderModel'] = relationship(back_populates='books')



    def __repr__(self):
        return f"<{self.booK_id}> {self.book_title} from {self.book_author}"

    def to_dict(self):
        return {"id": self.book_id, "title": self.book_title, "author": self.book_author}

class BooksResources(Resource):
    def post(self):
        data = request.get_json()
        new_book = BookModel(**data)
        db.session.add(new_book)
        db.session.commit()
        return new_book.to_dict(), 201

    def get(self):
        books = db.session.execute(db.select(BookModel)).scalars()
        return [b.as_dict() for b in books]
        # books = [book.to_dict() for book in db.session.query(BookModel).all()] # това е синтаксис от SQLAlchemy V2
        # return books
        # друг вариянт е:
        # books = BookModel.query.all()
        # return [b.as_dict() for b in books]

class SingleBookResources(Resource):
    def get(self, book_id):
        pass
    def put(self, book_id):
        pass
    def delete(self, book_id):
        pass



class ReaderModel(db.Model):
    __tablename__ = 'readers' # readers e imeto na tablicata i tova ime se izpolzva gore vyv ForeignKey('readers.id') демек,
    # в буукмодел колоната reader_id ще вземе поредния номера на reader-a от таблицата readers.

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    books: Mapped[list['BookModel']] = relationship(back_populates='reader') # това доколкото разбирам ще е графа в новта таблица, която ще показва, даден
    # читател кой книги има на негово име.


api.add_resource(BooksResources, '/books')
api.add_resource(SingleBookResources, "/books/<int:id>")

# with app.app_context():
#     db.create_all()

 