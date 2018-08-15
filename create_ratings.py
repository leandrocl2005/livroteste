from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
import os

# Set up online DATABASE_URL
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("""
	CREATE TABLE ratings (
		id SERIAL PRIMARY KEY,
		review VARCHAR NOT NULL,
		rating INTEGER NOT NULL,
		user_id INTEGER REFERENCES users,
		book_id INTEGER REFERENCES books
	);""")
db.commit()
