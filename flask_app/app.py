from flask import Flask, render_template, session, flash, redirect, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# Update imports to include new models
from setup_db import User, ToDo, Assessment, StudySession, CoCurricular, PersonalCommitment
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if username already exists
        existing_user = db_session.query(User).filter_by(username=username).first()
        if (existing_user):
            flash('Username already exists', 'danger')
            return redirect('/signup')

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect('/signup')

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db_session.add(new_user)
        db_session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect('/login')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect('/')

@app.route('/add_todo', methods=["POST"])
def add_todo():
    # Ensure the user is logged in
    if "user_id" not in session:
        flash("Please log in to add a to-do.", "warning")
        return redirect('/login')
    
    # Retrieve task data from the form
    task = request.form.get("task")
    user_id = session["user_id"]
    
    # Create a new ToDo object and save it to the database
    new_todo = ToDo(task=task, user_id=user_id)
    db_session.add(new_todo)
    db_session.commit()
    
    flash("To-Do added successfully!", "success")
    return redirect('/dashboard')

@app.route('/update_todo/<int:todo_id>', methods=["POST"])
def update_todo(todo_id):
    # Ensure the user is logged in
    if "user_id" not in session:
        flash("Please log in to update a to-do.", "warning")
        return redirect('/login')
    
    # Retrieve the new task name from the form
    new_task = request.form.get("new_task")
    
    # Query the database for the to-do
    todo = db_session.query(ToDo).get(todo_id)
    
    # Ensure the to-do exists and belongs to the logged-in user
    if todo and todo.user_id == session["user_id"]:
        # Update the task name
        todo.task = new_task
        db_session.commit()
        flash("To-Do updated successfully!", "success")
    else:
        flash("To-Do not found or access denied.", "danger")
    
    return redirect('/dashboard')
    

@app.route('/delete_todo/<int:todo_id>', methods=["POST"])
def delete_todo(todo_id):
    # Ensure the user is logged in
    if "user_id" not in session:
        flash("Please log in to delete a to-do.", "warning")
        return redirect('/login')
    
    # Query the database for the to-do and delete it
    todo = db_session.query(ToDo).get(todo_id)
    
    # Ensure the to-do exists and belongs to the logged-in user
    if todo and todo.user_id == session["user_id"]:
        db_session.delete(todo)
        db_session.commit()
        flash("To-Do deleted successfully!", "success")
    else:
        flash("To-Do not found or access denied.", "danger")
    
    return redirect('/dashboard')

@app.route('/assessments')
def assessments():
    if "user_id" not in session:
        flash("Please log in to view assessments.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    user_assessments = db_session.query(Assessment).filter_by(user_id=user_id).all()
    return render_template('assessments.html', assessments=user_assessments)

@app.route('/study_sessions')
def study_sessions():
    if "user_id" not in session:
        flash("Please log in to view study sessions.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    user_sessions = db_session.query(StudySession).filter_by(user_id=user_id).all()
    return render_template('study_sessions.html', sessions=user_sessions)

@app.route('/co_curricular')
def co_curricular():
    if "user_id" not in session:
        flash("Please log in to view co-curricular activities.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    activities = db_session.query(CoCurricular).filter_by(user_id=user_id).all()
    return render_template('co_curricular.html', activities=activities)

@app.route('/personal_commitments')
def personal_commitments():
    if "user_id" not in session:
        flash("Please log in to view personal commitments.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    commitments = db_session.query(PersonalCommitment).filter_by(user_id=user_id).all()
    return render_template('personal_commitments.html', commitments=commitments)

@app.route('/todos')
def todos():
    if "user_id" not in session:
        flash("Please log in to view todos.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    user_todos = db_session.query(ToDo).filter_by(user_id=user_id).all()
    return render_template('add_todo.html', todos=user_todos)

if __name__ == '__main__':
    app.run(debug=True)
