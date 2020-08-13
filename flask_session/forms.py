from wtforms import Form, StringField, SelectField
class BookSearchForm(Form):
    choices = [('Title', 'title'),
               ('Author', 'author'),
               ('Year', 'year'),
               ('ISBN', 'isbn'),
               ]
    select = SelectField('Search for books:', choices=choices)
    search = StringField('')