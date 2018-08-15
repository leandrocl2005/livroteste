from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
import os

# Set up local DATABASE_URL
#user = 'postgres'
#password = 'root1234'
#host = 'localhost'
#port = '5432'
#db = 'lecture3'
#url = 'postgresql://{}:{}@{}:{}/{}'
#url = url.format(user, password, host, port, db)
#engine = create_engine(url, client_encoding='utf8')
#db = scoped_session(sessionmaker(bind=engine))

# Set up online DATABASE_URL
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("""
	CREATE TABLE books (
		id SERIAL PRIMARY KEY,
		title VARCHAR NOT NULL,
		author VARCHAR NOT NULL,
		ISBN VARCHAR NOT NULL,
		publication_year INTEGER NOT NULL
	);""")
db.commit()

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)
    for isbn, title, author, publication_year in reader:
        db.execute("""
        	INSERT INTO books (title, author, isbn, publication_year)
        		VALUES (:title, :author, :isbn, :publication_year)""",
        	{
        		"title": title,
        		"author": author,
        		"isbn": isbn,
        		"publication_year": int(publication_year)
        	})
    db.commit()
    print("Success")
    f.close()

if __name__ == "__main__":
    main()


