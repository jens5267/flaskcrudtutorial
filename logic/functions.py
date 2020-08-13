import csv

from flask import  request, redirect, render_template

def get_books(Book, db):
    with open('books.csv') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        books = []
        for isbn, title, author, year in reader:
            if line_count == 0:
                line_count += 1
            else:
                books.append({'title': title, 'year': year, 'author': author, 'isbn': isbn})
                line_count += 1

        return books


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def delete(db, obj_to_delete, redirect_route, obj):
    try:
        db.session.delete(obj_to_delete)
        db.session.commit()
        return redirect(redirect_route)
    except:
        return f"There was a problem deleting that {obj}"