from decouple import config
from flask import Flask, request # Flask e class, koito idva ot modula flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import  Resource, Api
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from flask_migrate import Migrate
from werkzeug.exceptions import NotFound
from Exceptions import *

app = Flask(__name__) # tova ni e nachalaoto na samiq flask app
db_user = config('DB_USER')
db_password = config('DB_PASS')
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_name = config('DB_NAME')


app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{db_user}:"
                                         f"{db_password}@"
                                         f"{db_host}:"
                                         f"{db_port}/"
                                         f"{db_name}")


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
    book_title: Mapped[str] = mapped_column(String(100),unique=True, nullable=False)
    book_author: Mapped[str] = mapped_column(String(50), nullable=False)

    reader_id: Mapped[int] = mapped_column(ForeignKey('readers.reader_id'), nullable=True)
    reader_name: Mapped[str] = mapped_column(String(50), nullable=True)

    reader: Mapped['ReaderModel'] = relationship(back_populates='books')

    def __repr__(self):
        return f"<{self.booK_id}> {self.book_title} from {self.book_author}"

    def to_dict(self):
        return {"id": self.book_id, "title": self.book_title, "author": self.book_author, "reader_id": self.reader_id}

class BooksResources(Resource):

    def get(self):
        books = db.session.execute(db.select(BookModel)).scalars()
        return [b.to_dict() for b in books]
        # books = [book.to_dict() for book in db.session.query(BookModel).all()] # това е синтаксис от SQLAlchemy V2
        # return books
        # друг вариянт е:
        # books = BookModel.query.all()
        # return [b.as_dict() for b in books]

    def post(self):
        data = request.get_json()
        new_book = BookModel(**data)
        try:
            db.session.add(new_book)
            db.session.commit()
        except IntegrityError:
            return {"message": "Book already exists"}, 400
        return new_book.to_dict(), 201

class SingleBookResources(Resource):
    def get(self, book_id):
        try:
            current_book = db.session.execute(db.select(BookModel).filter_by(book_id = book_id)).scalar_one()
            return current_book.to_dict(), 200
        except NoResultFound:
            return {"message": "Book not found"}

    def put(self, book_id):
        data = request.get_json()

        try:
            current_reader = db.session.execute(db.select(ReaderModel).filter_by(reader_email = data['reader_email'])).scalar_one()
        except NoResultFound:
            return {"message": f"Reader with e-mail address {data['reader_email']} not found"}

        try:
            current_book = db.session.execute(db.select(BookModel).filter_by(book_id=book_id)).scalar_one()
            if not current_book.reader_id:
                current_book.reader_id = current_reader.reader_id
                current_book.reader_name = current_reader.reader_name
                db.session.commit()
                return current_book.to_dict(), 201
            else:
                return {"message": f"Reader {current_book.reader_name} with reader id:{current_book.reader_id} already assigned to this book"}, 400
        except NoResultFound:
            return {"message": f"Book with id:{book_id} not found"}

    def delete(self, book_id):
        try:
            current_book = db.session.execute(db.select(BookModel).filter_by(book_id=book_id)).scalar_one()
            db.session.delete(current_book)
            db.session.commit()
            return f'{current_book.book_title} with id:{current_book.book_id} deleted!'
        except NoResultFound:
            return {"message": f"Book with id:{book_id} not found!"}



class ReaderModel(db.Model):
    __tablename__ = 'readers' # readers e imeto na tablicata i tova ime se izpolzva gore vyv ForeignKey('readers.id') демек,
    # в буукмодел колоната reader_id ще вземе поредния номера на reader-a от таблицата readers.

    reader_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reader_name: Mapped[str] = mapped_column(String(80), unique=False, nullable=False)
    reader_email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    books: Mapped[list['BookModel']] = relationship(back_populates='reader') # това доколкото разбирам ще е графа в новта таблица, която ще показва, даден
    # читател кой книги има на негово име.

    def __repr__(self):
        return f"{self.reader_id} {self.reader_name} with {self.reader_email}"

    def to_dict(self):
        return {"id": self.reader_id, "name": self.reader_name, "email": self.reader_email}

class ReadersResources(Resource):

    def get(self):
        readers = db.session.execute(db.select(ReaderModel)).scalars()
        return [r.to_dict() for r in readers]

    def post(self):
        data = request.get_json()
        new_reader = ReaderModel(**data)

        try:
            db.session.add(new_reader)
            db.session.commit()
            return new_reader.to_dict(), 201
        except IntegrityError:
            return {"message": "Book already exists"}, 400

class SingleReaderResources(Resource):
    pass
    # check to create a singlereader class and create a function to check if the reader already exists in readers
    # and if not create such function and then once checked modify the single book.

api.add_resource(BooksResources, '/books')
api.add_resource(SingleBookResources, "/books/<int:book_id>")

api.add_resource(ReadersResources, '/readers')
api.add_resource(SingleReaderResources, "/readers/<int:reader_id>")


# with app.app_context():
#     db.create_all()

 