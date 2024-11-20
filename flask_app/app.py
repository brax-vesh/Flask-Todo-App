from flask import Flask, render_template, session, flash, redirect, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from setup_db import User, ToDo
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = "supersecretkey"
# Replace with a secure, random key in production

# Create the engine and session
engine = create_engine('sqlite:///todo.db')
Session = sessionmaker(bind=engine)
db_session = Session()

# Create the tables
# Base.metadata.create_all(engine)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect('/login')
    # Retrieve the user's to-dos from the database

    user_id = session["user_id"]
    user = db_session.query(User).get(user_id)
    return render_template('dashboard.html', todos=user.todos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db_session.query(User).filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            print("Login successful!", "info")
            return redirect(('/dashboard'))
        else:
            print("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
