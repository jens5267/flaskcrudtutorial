import os

from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content= db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template('base.html')

@app.route("/test", methods=['POST', 'GET'])
def test():
    print(request)
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('test')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('testsites/test.html', tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/test')
    except:
        return 'There was a problem deleting that task'

@app.route("/update/<int:id>", methods=['POST', 'GET'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/test')
        except:
            return 'There was a problem updating that task'
    else:
        return render_template('update.html', task=task)


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