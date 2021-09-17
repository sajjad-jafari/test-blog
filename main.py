from flask import Flask, render_template, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm,registerForm,loginForm,commentForm
from flask_gravatar import Gravatar
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager=LoginManager(app)


def is_admin(function):
    @wraps(function)
    def wrapper():
        if current_user.id == 1:
            return function()
        else:
            print('you are not shit')
    return wrapper



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
##CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id=db.Column(db.Integer,db.ForeignKey('blog_members.id'))
    author=db.relationship('User',back_populates='posts')
    comments=db.relationship('Comment',back_populates='parent_post')


class User(db.Model,UserMixin):
    __tablename__="blog_members"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(100),nullable=False, unique=True)
    password=db.Column(db.String(),nullable=False)
    posts = db.relationship('BlogPost', back_populates='author')
    comments=db.relationship('Comment', back_populates='commenter')

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(2000),nullable=False)
    commenter=db.relationship('User', back_populates='comments')
    commenter_id=db.Column(db.Integer,db.ForeignKey('blog_members.id'))
    parent_post=db.relationship('BlogPost', back_populates='comments')
    post_id=db.Column(db.Integer,db.ForeignKey('blog_posts.id'))


    def __repr__(self):
        return self.name


db.create_all()

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=['POST','GET'])
def register():
    form = registerForm()
    if request.method=='POST':
        email=form.email.data
        name=form.name.data
        password=form.password1.data
        password_hash=generate_password_hash(password,salt_length=8,method='pbkdf2:sha256')
        user_to_create=User(email=email,password=password_hash,name=name)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form=form)


@app.route('/login', methods=['POST','GET'])
def login():
    form=loginForm()
    if request.method=='POST':
        email=form.email.data
        password=form.password1.data
        found_user=User.query.filter_by(email=email).first()
        if found_user:
            if check_password_hash(found_user.password,password):
                print('welcome')
                login_user(found_user)
                flash("You logged in")
            else:
                print('Wrong!')

    return render_template("login.html",form=form)


@app.route('/logout')
def logout():
    posts=User.query.get(1).posts
    print(posts)
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST','GET'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    comments=requested_post.comments
    form=commentForm()
    if request.method=='POST':
        comment_to_add=Comment(body=form.comment.data,parent_post=requested_post,commenter=current_user)
        db.session.add(comment_to_add)
        db.session.commit()

    return render_template("post.html", post=requested_post,comments=comments,form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post",methods=['POST','GET'])
@login_required
@is_admin
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            author=current_user,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
