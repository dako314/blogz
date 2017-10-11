from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body
    


@app.route('/blog', methods=['POST', 'GET'])
def index():
    
    form_value = request.args.get('id')

    if request.method == 'POST':
        title_error = ''
        body_error = ''
      
        blog_title = request.form['title']
        blog_body = request.form['body']


        if blog_title == '':
            title_error = "Please enter a blog title!" 

        if blog_body == '':
            body_error = "A blog entry should not be empty!"


        if not title_error and not body_error:      
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.filter_by(title=blog_title).first()
            return redirect('/blog?id={0}'.format(blog.id))
        
        else:
            return render_template('newpost.html', title="My Blog!", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    if request.method == 'GET' and form_value:
        blog = Blog.query.get(form_value)
        return render_template('single.html', title="My Blog", blog=blog)        
   
    
    blogs = Blog.query.all()  
    return render_template('blog.html',title="My Blog!", blogs=blogs)        

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html', title="My Blog!")


if __name__ == '__main__':
    app.run()