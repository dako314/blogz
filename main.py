from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

#pylint: disable=no-member

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods = ['GET', 'POST'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if request.method == 'POST':
        new_post_title = request.form['title'].strip()
        new_post_body = request.form['body'].strip()
        new_post_owner_id = request.form['owner_id']
        owner = User.query.filter_by(id = new_post_owner_id).first()
        if (not new_post_title) or (not new_post_body):
            error = "Something went wrong. Please try again."
            return render_template('add-blog.html',  title = 'Build-a-Blog', post_title = new_post_title, post_body = new_post_body, error = error)
        post = Blog(new_post_title, new_post_body, owner)
        db.session.add(post)
        db.session.commit()
        return redirect('/blog?id='+str(post.id))

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('display-post.html', title = post.title, post = post)

    if user_id:
        posts = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('singleUser.html', posts = posts)

    return render_template('blog.html', title = "Blogz", posts = Blog.query.all())

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username = ""
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        verify = request.form['verify'].strip()

        # Use this to check if username already exists.
        user = User.query.filter_by(username = username).first()

        if not username or not password or not verify:
            flash('One or more fields are invalid', 'error')

        elif user:
            flash('Username already exists.', 'error')

        elif password != verify:
            flash('Passwords do not match.', 'error')

        elif len(password) < 3 or len(username) < 3:
            flash('Invalid username or invalid password.', 'error')

        else: # If everything is valid, add the user.
            user = User(username, password)
            session['username'] = username
            db.session.add(user)
            db.session.commit()
            return redirect('/newpost')

    return render_template('signup.html', username = username)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    username = ""

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in.')
            return redirect('/newpost')
        elif not user:
            flash('Username does not exist.', 'error')
            username = ""
        else: 
            flash('Incorrect password.', 'error')

    return render_template('login.html', username = username)


@app.route('/logout')
def logout():
    # Delete username from session.
    del session['username']
    return redirect('/blog')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title = "Blogz", users = users)


@app.route('/newpost')
def display():
    # TODO: We need to do something here; possibly passing the owner?
    username = session['username']
    owner = User.query.filter_by(username = username).first()
    # TODO: Edit html so query parameters include owner.id
    return render_template('add-blog.html', title = 'Build-a-Blog', owner = owner)


if __name__ == '__main__':
    app.run()