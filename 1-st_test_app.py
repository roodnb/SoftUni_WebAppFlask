from symtable import Class

from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import NotFound

app = Flask(__name__)
api = Api(app)

class BookModel:
    def __init__(self, title, author, id):
        self.title = title
        self.author = author
        self.id = id

    def __str__(self):
        return f"Title: {self.title}, Author: {self.author}, ID: {self.id}"

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}



books = [BookModel(f"Title {num}", f"Author {num}", num) for num in range(1, 6)]

# its important that the method names are the same as name as the requests, for example it can not be gett or posttt etc.
class BooksResource(Resource):
    def get(self):
        return [book.to_dict() for book in books]

    def post(self):
        data = request.get_json() # tozi, koito izprashta requesta za trqbva da dade danni za novata kniga. Tazi data idva ot centralen obekt ,
                                 # kojto se kazva request(importva se ot Flask) i toi nosi cqloto znanie za samiq request.Kakyv e motoda , dali ima danni kym tozi request i t.n.
                                # Realno promenlivata data shte pazi v sebe si tova koeto se podava ot vynka , tova koeto se nosi s post request-a.
                                # Drugo vajno tuk e che datata podavaiki se kato json realno python q interpretira kato dictionary i trqbva da se razarhivira.
        next_id = books[-1].id + 1
        new_book = BookModel(data["title"], data["author"], next_id) # or BookModel(**data, id) - we unarchive the data object which is a key value pair.
        books.append(new_book)
        return new_book.to_dict()


class SingleBookResource(Resource):
    def get(self, id):
        try:
            current_book = [cur_b for cur_b in books if cur_b.id == id][0] # въртим try except защото може и да ни подадат кофти ид , което го няма в листа
            return current_book.to_dict()
        except IndexError:
            raise NotFound()

    def put(self, id):
        data = request.get_json() # dannite koito shte se izpratqt na put requesta.
        try:
            current_book = [cur_b for cur_b in books if cur_b.id == id][0]
            current_book.title = data["title"]
            return current_book.to_dict()
        except IndexError:
            return {"message": "Book not found"}, 404

    def delete(self, id):
        try:
            current_book = [cur_b for cur_b in books if cur_b.id == id][0]
            books.remove(current_book)
            return 204
        except IndexError:
            return {"message": "Book not found"}, 404


api.add_resource(BooksResource, "/books")
api.add_resource(SingleBookResource, "/books/<int:id>") # toq int idva ot samia Flask za da moje flask da go razbere kato integer a ne kato string