from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
import os

# Set up online DATABASE_URL
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#db.execute("""
#	CREATE TABLE users (
#		id SERIAL PRIMARY KEY,
#		username VARCHAR NOT NULL,
#		password VARCHAR NOT NULL
#	);""")
#db.commit()

db.execute("""
	INSERT INTO users
		(username,password)
		VALUES ('leandro','1234');
""")
db.commit()

