import csv

with open('books.csv') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for isbn,title,author,year in reader:
        if line_count == 0:
            print(f'Column names are {isbn},{title},{author},{year}')
            line_count += 1
        elif line_count < 50:
            print(f'Booktitle: {title}, Author: {author}, ISBN: {isbn}, published in {year}')
            line_count += 1