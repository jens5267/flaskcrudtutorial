import os
import pdfkit


from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    make_response,
    Response
)
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

# import flask_whooshalchemy as wa

from datetime import datetime
from logic.functions import get_books, get_or_create, delete

from os import walk
from zipfile import ZipFile

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = 'supersecret'
app.config['WHOOSH_BASE'] = 'whoosh'
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # done = db.Column(db.Boolean, default=0)

    def __repr__(self):
        return "<Task %r>" % self.id


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=0)
    rated = db.Column(db.Integer, default=0)
    total_rating = db.Column(db.Float, default=0)
    average_rating = db.Column(db.Float, default=0)

    def __repr__(self):
        return "<Book %r>" % self.id


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField(
        'Email', validators=[InputRequired(),
        Email(message='Invalid email'), Length(max=50)])
    username = StringField(
        'Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField(
        'Password', validators=[InputRequired(), Length(min=8, max=80)])


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80), unique=True)

# wa.whoosh_index(app, Book)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# to create/ update db: python -> from application import db -> db.create_all()
# otherwise: flask db init -> flask db migrate -> flask db upgrade
# checkout databas: sqlite3 test.db -> see tables: .table -> select * from user;

@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    return render_template("base.html")


@app.route("/test", methods=["POST", "GET"])
@login_required
def add_task():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("test")
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("testsites/test.html", tasks=tasks)


@app.route("/task/update/<int:id>", methods=["POST", "GET"])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/test")
        except:
            return "There was a problem updating that task"
    else:
        return render_template("update.html", task=task)

@app.route("/task/delete/<int:id>", methods=["POST", "GET"])
@login_required
def delete_task(id):
    task_to_delete = Todo.query.get_or_404(id)
    redirect_route = "/test"
    return delete(db, task_to_delete, redirect_route, 'Task')

@app.route("/books", methods=["POST", "GET"])
@login_required
def add_book():
    if request.method == "POST":
        book_title = request.form["title"]
        book_author = request.form["author"]
        book_year = request.form["year"]
        book_isbn = request.form["isbn"]
        new_book = Book(
            title=book_title, author=book_author, year=book_year, isbn=book_isbn
        )
        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect("books")
        except:
            return "There was an issue adding your book"
    else:
        books = Book.query.order_by(Book.title).all()
        return render_template("book/books.html", books=books, name=current_user.username)


@app.route("/book/rate/<int:id>", methods=["POST", "GET"])
# @login_required
def rate_book(id):
    book = Book.query.get_or_404(id)

    if book.rated == None:
        book.rated = 0
    if book.average_rating == None:
        book.average_rating = 0
    if book.total_rating == None:
        book.total_rating = 0
    if request.method == "POST":
        book.rating = request.form['rate']
        book.rated += 1
        book.total_rating += int(book.rating)
        book.average_rating = f'{book.total_rating / book.rated:0.2f}'
        try:
            db.session.commit()
            return redirect("/books")
        except:
            return "There was a problem rating that book"
    # print(book)
    # print(rating)
    # print(current_user.username)
    return redirect(f"/book/update/"+str(id))

@app.route("/book/update/<int:id>", methods=["POST", "GET"])
@login_required
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == "POST":
        book.title = request.form["title"]
        book.author = request.form["author"]
        book.year = request.form["year"]
        book.isbn = request.form["isbn"]
        try:
            db.session.commit()
            return redirect("/books")
        except:
            return "There was a problem updating that book"
    else:
        return render_template("/book/update.html", book=book)

@app.route('/book/delete/<int:id>', methods=["POST", "GET"])
@login_required
def delete_book(id):
    book_to_delete = Book.query.get_or_404(id)
    redirect_route = "/books"
    return delete(db, book_to_delete, redirect_route, 'Book')

@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    books = get_books(Book, db)
    books_isbn_in_db = [b.isbn for b in Book.query.all()]

    for book in books:
        new_book = Book(
            title=book["title"],
            author=book["author"],
            year=book["year"],
            isbn=book["isbn"],
        )

        if not new_book.isbn in books_isbn_in_db:
            try:
                db.session.add(new_book)
                db.session.commit()
            except:
                return "There was an issue adding your book"

    return redirect("/books")

@app.route("/delete_all", methods=["POST", "GET"])
@login_required
def delete_all():
    books = Book.query.all()
    for book in books:
        db.session.delete(book)
        db.session.commit()
    return redirect("/books")

def get_or_create(model, **kwargs):
    try:
        obj = db.session.query(model).filter(**kwargs).first()
        return obj
    except:
        obj = model()
        return obj

@app.route("/login2", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/books')
        return '<h1>invalid username or password</h1>'
    return render_template('user/login2.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login2")


@app.route("/register2", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            )
        db.session.add(new_user)
        db.session.commit()
        return '<h1> New User has been created </h1>'
    return render_template('user/register2.html', form=form)

@app.route("/search", methods=["POST", "GET"])
def search():
    search = Book.query.whoosh_search(request.args.get('query')).all()
    return render_template("book/books.html", books=books)
# @app.route("/register", methods=["POST", "GET"])
# def register():
#     print('register')
#     form = RegisterForm()
#     print('form', form.email)
#     if form.validate_on_submit():
#         return '<h1>' + form.username.data + '</h1>'

#     return render_template('user/register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)


# app.config['DATABASE_URL']='postgres://gklqqjfmmscgcv:e1df67db09a2d236d3cbdefb7d33d7cea6f2526c461fc29488140bd55ceda586@ec2-176-34-123-50.eu-west-1.compute.amazonaws.com:5432/dadg7jsstqspq7'

# from flask_session import Session
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker


# users = []
# users.append(User(id=1, username='Anthony', password='password'))
# users.append(User(id=2, username='Becca', password='secret'))
# users.append(User(id=3, username='Carlos', password='somethingsimple'))

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session.pop('user_id', None)

#         username = request.form['username']
#         password = request.form['password']
#         try:
#             user = [x for x in users if x.username == username][0]
#         except IndexError:
#             user = None
#         print('user', user)
#         if user and user.password == password:
#             session['user_id'] = user.id
#             return redirect(url_for('profile'))

#         return redirect(url_for('login'))
#     return render_template('user/login.html')

# @app.route("/profile")
# def profile():
#     return render_template('profile.html')

# @app.route("/register")
# def register():
#     return render_template('user/register.html')

# goodreads.com/api/keys
# application name: project1-find-your-book
# company name: CS50
# key: 7tz7KJHhLbymfcF9Mwvjw
# secret: YyC9WFF9ye7w6tLHL5bwtin3B5L8FNCZQZCT3xIrdU

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.username


# @app.route("/download_book_info", methods=['POST', 'GET'])
# def download():
#     pdfs = []
#     books = Book.query.all()
#     css = ['templates/downloads/pdf_style.css']
#     for (dirpath, dirnames, filenames) in walk('templates/downloads'):
#         for filename in filenames:
#             # pdfs.append(dirpath+'/'+filename)
#             print('here', dirpath[10:]+'/'+filename)
#             rendered = render_template(dirpath[10:]+'/'+filename, books=books)
#             print('rendered')
#             pdf = pdfkit.from_string(rendered, False, css=css)
#             print('pdf')
#             pdfs.append(pdf)

#     response = make_response(pdfs)
#     # response = Response(pdfs, mimetype='application/pdf')
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

#     return response
