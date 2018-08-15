import os
from flask import render_template, request, make_response
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import abort
import json

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up online database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET','POST'])
def login():
	return render_template("login.html")

@app.route('/auth/login', methods=['GET','POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

	# make sure username and password exists
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        session['username'] = None
        return render_template("error.html", message="Username or password incorrect.")
    else:    
    	session['username'] = username
    return render_template("search.html", username=session['username'])

@app.route('/register')
def register_template():
    return render_template('register.html')

@app.route('/auth/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
    	return render_template("error.html", message="Username already exists.")
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
        {"username": username, "password": password})
    db.commit()
    session['username'] = username
    return render_template("index.html", username=session['username'])

@app.route('/logout')
def logout_template():
	return render_template("logout.html", username=session['username'])

@app.route('/auth/logout')
def logout_user():
    if session:
    	session.clear()
    return render_template('index.html',username=session['username'])

@app.route('/search', methods=['GET','POST'])
def search_template():
	if session:
		return render_template('search.html',username=session['username'])
	return render_template("login.html")

@app.route('/search/results', methods=['GET','POST'])
def search_results():
    name = request.form['name']
    if db.execute("SELECT * FROM books WHERE title LIKE :a",{'a':'%'+name+'%'}).rowcount==0:
        if db.execute("SELECT * FROM books WHERE isbn LIKE :a",{'a':'%'+name+'%'}).rowcount==0:
            if db.execute("SELECT * FROM books WHERE author LIKE :a",{'a':'%'+name+'%'}).rowcount==0:
                return render_template('error.html',message='Not found')
            else:
            	books = db.execute("SELECT * FROM books WHERE author LIKE :a",{'a':'%'+name+'%'}).fetchall()
            	return render_template('results.html',books=books)
        else:
        	books = db.execute("SELECT * FROM books WHERE isbn LIKE :a",{'a':'%'+name+'%'}).fetchall()
        	return render_template('results.html',books=books)
    else:
        books = db.execute("SELECT * FROM books WHERE title LIKE :a",{'a':'%'+name+'%'}).fetchall()
        return render_template('results.html',books=books)

@app.route('/book_page/<int:book_id>')
def book_page(book_id):
	book = db.execute("SELECT * FROM books WHERE id = :book_id",{'book_id':book_id}).fetchone()
	reviews = db.execute("SELECT * FROM ratings WHERE book_id = :book_id",{'book_id':book_id}).fetchall()
	media = "{:.2f}".format(db.execute("SELECT AVG(rating) FROM ratings WHERE book_id = :book_id", {'book_id':book_id}).fetchone()[0])
	ctx = {
		'book': book,
		'reviews': reviews,
		'media': media
	}
	return render_template("book_page.html", ctx=ctx)

@app.route('/make_review/<int:book_id>')
def make_review(book_id):
	return render_template('make_review.html',book_id=book_id)

@app.route('/auth/review/<int:book_id>',methods=['GET','POST'])
def review_save(book_id):
	user =  db.execute("SELECT id FROM users WHERE username = :username",{'username':session['username']}).fetchone()
	user_id = user['id']
	book_id = book_id
	review = request.form['review']
	rating = request.form['rating']
	db.execute("INSERT INTO ratings (review, rating, user_id, book_id) VALUES (:review, :rating, :user_id, :book_id)",
        {"review": review, "rating": rating, "user_id":user_id, "book_id":book_id})
	db.commit()
	return render_template("index.html",username=session['username'])

@app.route('/api/<string:isbn>')
def isbn_api(isbn):
	if db.execute("SELECT * FROM books WHERE isbn = :isbn",{'isbn':isbn}).rowcount==0:
	    abort(404)
	else:
		book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{'isbn':isbn}).fetchone()
		reviews = db.execute("SELECT * FROM ratings WHERE book_id = :book_id",{'book_id':book.id}).fetchall()
		review_count = len(reviews)
		media = "{:.2f}".format(db.execute("SELECT AVG(rating) FROM ratings WHERE book_id = :book_id", {'book_id':book.id}).fetchone()[0])
		ctx = {
			'title': book.title,
			'author': book.author,
			'year': book.publication_year,
			'isbn': book.isbn,
			'review_count': review_count,
			'average_score': media
		}

		return json.dumps(ctx)

# DATABASE_URL = https://data.heroku.com/datastores/0805d68f-3ffe-4626-bb44-cfe70442d689

