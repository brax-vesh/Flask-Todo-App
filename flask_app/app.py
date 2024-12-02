from flask import Flask, render_template, session, flash, redirect, request, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from setup_db import User, ToDo, Base  # Add Base to imports
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta  # Add date and timedelta to imports

app = Flask(__name__)

app.secret_key = "supersecretkey"
# Replace with a secure, random key in production

# Create the engine and session

#establishes connection to database
engine = create_engine('sqlite:///todo.db')

#session allows user to interact with the database
Session = sessionmaker(bind=engine)
db_session = Session()

# Create all tables
Base.metadata.create_all(engine)  # Uncomment this line to create tables

# Function to calculate days remaining, used on dashbaord and category pages
def calculate_days_remaining(due_date):
    if not due_date:
        return None
    today = date.today()
    days = (due_date.date() - today).days
    if days < 0:
        return "Overdue"
    elif days == 0:
        return "Due today"
    else:
        return f"{days} days left"

def calculate_days(due_date):
    if not due_date:
        return None
    
    today = datetime.now().date()
    days_remaining = (due_date.date() - today).days
    
    if days_remaining < 0:
        return 'Overdue'
    elif days_remaining == 0:
        return 'Due today'
    else:
        return f'{days_remaining} days left'

# Register the function as a template filter
app.jinja_env.globals['calculate_days'] = calculate_days

#home page - allows user to choos to login or signup
@app.route('/')
def home():
    return render_template('index.html')

#after user has logged in, they will be redirected to the dashboard, only able to be reached if logged in
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect('/login')

    user_id = session["user_id"]
    todos = db_session.query(ToDo).filter_by(user_id=user_id).all()
    return render_template('dashboard.html', todos=todos, calculate_days=calculate_days_remaining)

#Posts the entered username and password to the database, if the username and password match, the user is logged in
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

#how the user creates an account, if the username already exists, the user will be told to try again
#posts the username and password to the database
#redirects to login page after account is created so user can login using new credentials
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

# removes user id from the session, logging them out of their acc, and redirects them to the home page
@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect('/')

#allows user to add a to-do, if user is not logged in, they will be told to log in
#posts user entered data from add_todo field to database under their user id
@app.route('/add_todo', methods=["GET", "POST"])
def add_todo():
    if "user_id" not in session:
        flash("Please log in to add a to-do.", "warning")
        return redirect('/login')
    
    if request.method == "POST":
        task = request.form.get("task")
        category = request.form.get("category")
        due_date_str = request.form.get("due_date")
        user_id = session["user_id"]
        
        # Convert date string to datetime object if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash("Invalid date format", "error")
                return redirect('/add_todo')
        
        new_todo = ToDo(task=task, category=category, user_id=user_id, due_date=due_date)
        db_session.add(new_todo)
        db_session.commit()
        
        flash("To-Do added successfully!", "success")
        return redirect(url_for(category.lower().replace('-', '_').replace(' ', '_')))
    
    # Get the category from URL parameter
    default_category = request.args.get('category', '')
    return render_template('add_todo.html', default_category=default_category)

#allows user to update a to-do, if user is not logged in, they will be told to log in
#posts user entered data from update_todo field to database 
# new data replaces old data of the todo they selected to update
@app.route('/update_todo/<int:todo_id>', methods=["GET", "POST"])
def update_todo(todo_id):
    if "user_id" not in session:
        flash("Please log in to update a to-do.", "warning")
        return redirect('/login')
    
    todo = db_session.query(ToDo).get(todo_id)
    
    if not todo or todo.user_id != session["user_id"]:
        flash("Todo not found or access denied.", "danger")
        return redirect('/dashboard')

    if request.method == "POST":
        new_task = request.form.get("new_task")
        new_category = request.form.get("category")
        due_date_str = request.form.get("due_date")
        
        # Convert date string to datetime object if provided
        if due_date_str:
            try:
                todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash("Invalid date format", "error")
                return redirect(url_for('update_todo', todo_id=todo_id))
        else:
            todo.due_date = None
        
        todo.task = new_task
        todo.category = new_category
        db_session.commit()
        
        flash("Todo updated successfully!", "success")
        return redirect(url_for(new_category.lower().replace('-', '_').replace(' ', '_')))
    
    return render_template('update_todo.html', todo=todo)

#allows user to delete a to-do, if user is not logged in, they will be told to log in
#just removes the selected to-do from the database
@app.route('/delete_todo/<int:todo_id>', methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        flash("Please log in to delete a to-do.", "warning")
        return redirect('/login')
    
    todo = db_session.query(ToDo).get(todo_id)
    
    if todo and todo.user_id == session["user_id"]:
        db_session.delete(todo)
        db_session.commit()
        flash("To-Do deleted successfully!", "success")
    else:
        flash("To-Do not found or access denied.", "danger")
    
    # Return to the previous page using request.referrer
    return redirect(request.referrer or '/dashboard')

#allows user to toggle a to-do, if user is not logged in, they will be told to log in
#changes the status of the selected to-do from completed to not completed or vice versa
# will not remove the todo just displays it as completed, crossed off the list

@app.route('/toggle_todo/<int:todo_id>', methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        flash("Please log in to update a to-do.", "warning")
        return redirect('/login')
    
    todo = db_session.query(ToDo).get(todo_id)
    
    if todo and todo.user_id == session["user_id"]:
        todo.completed = not todo.completed
        db_session.commit()
        flash("To-Do status updated successfully!", "success")
    else:
        flash("To-Do not found or access denied.", "danger")
    
    return redirect(request.referrer or '/dashboard')

#allows user to view all to-dos categorised in assessment category
#only able to be reached if logged in

@app.route('/assessments')
def assessments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todos = db_session.query(ToDo).filter_by(user_id=session['user_id'], category='Assessments').all()
    return render_template('assessments.html', todos=todos, calculate_days=calculate_days_remaining)

@app.route('/study_sessions')
def study_sessions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todos = db_session.query(ToDo).filter_by(user_id=session['user_id'], category='Study Sessions').all()
    return render_template('study_sessions.html', todos=todos, calculate_days=calculate_days_remaining)

@app.route('/co_curricular')
def co_curricular():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todos = db_session.query(ToDo).filter_by(user_id=session['user_id'], category='Co-Curricular').all()
    return render_template('co_curricular.html', todos=todos, calculate_days=calculate_days_remaining)

@app.route('/personal_commitments')
def personal_commitments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todos = db_session.query(ToDo).filter_by(user_id=session['user_id'], category='Personal Commitments').all()
    return render_template('personal_commitments.html', todos=todos, calculate_days=calculate_days_remaining)

#renders the add todo page, which allows users to add a to-do to their data base
@app.route('/todos')
def todos():
    if "user_id" not in session:
        flash("Please log in to view todos.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    user_todos = db_session.query(ToDo).filter_by(user_id=user_id).all()
    return render_template('add_todo.html', todos=user_todos)

#renders the all todos page, which allows users to view all of their to-dos in one page
@app.route('/all_todos')
def all_todos():
    if "user_id" not in session:
        flash("Please log in to view todos.", "warning")
        return redirect('/login')
    
    user_id = session["user_id"]
    todos = db_session.query(ToDo).filter_by(user_id=user_id).all()
    return render_template('all_todos.html', todos=todos)

if __name__ == '__main__':
    app.run(debug=True)
