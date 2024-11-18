from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash
from setup_db import User, ToDo
from flask import request, flash
from werkzeug.security import check_password_hash
from setup_db import Base, User, ToDo

app = Flask(__name__)

app.secret_key = "supersecretkey" # Replace with a secure, random key in production
# Set up the database engine and session

# Create the engine and session
engine = create_engine('sqlite:///todo.db')
Session = sessionmaker(bind=engine)
session = Session()

# # Create the tables
# Base.metadata.create_all(engine)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            print("Login successful!", "info")
        else:
            print("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
