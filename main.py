from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from forms import EmailForm, RegisterForm, LoginForm, CreateBlogPost, CommentForm, CreatePostForm
from contact import Contact


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RCA-Users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User database classes
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    blog_posts = relationship("BlogPost", back_populates="author")
    blog_comments = relationship("BlogComment", back_populates="blog_comment_author")
    message_posts = relationship("Message", back_populates="author")
    message_comments = relationship("MessageComment", back_populates="message_comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship("User", back_populates="blog_posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    blog_comments = relationship("BlogComment", back_populates="blog_parent_post")


class BlogComment(db.Model):
    __tablename__ = "blog_comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_comment_author = relationship("User", back_populates="blog_comments")
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    blog_parent_post = relationship("BlogPost", back_populates="blog_comments")
    blog_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship("User", back_populates="message_posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    message_comments = relationship("MessageComment", back_populates="message_parent_post")


class MessageComment(db.Model):
    __tablename__ = "message_comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_comment_author = relationship("User", back_populates="message_comments")
    message_post_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    message_parent_post = relationship("Message", back_populates="message_comments")
    message_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)


# Opens and creates database tables
with app.app_context():
    db.create_all()


# Decorator function that checks if current_user is Admin
def admin_only(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorator


# Searches database for authenticated user. Returns 404 status if user not in database.
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Authentication functions
@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    all_users = User.query.all()
    if login_form.validate_on_submit():
        for user in all_users:
            if login_form.email.data == user.email and check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return redirect(url_for("home"))
        if login_form.email.data != user.email:
            flash("That email does not exist. Please check the email and try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, login_form.password.data):
            flash("That password is incorrect. Please try again.")
            return redirect(url_for("login"))
    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    all_emails = [user.email for user in User.query.all()]
    reg_form = RegisterForm()
    if reg_form.validate_on_submit():
        if reg_form.email.data in all_emails:
            flash("You have already signed up with that email. Please login.")
            return redirect(url_for("login"))
        else:
            new_user = User(
                email=reg_form.email.data,
                password=generate_password_hash(reg_form.password.data, 'pbkdf2:sha256', 8),
                name=reg_form.name.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=reg_form)


# About page
@app.route("/about")
def about_us():
    return render_template("about.html")


# Contact page
@app.route("/contact")
def contact():
    contact_form = EmailForm()
    if contact_form.validate_on_submit():
        new_message = Contact(contact_form.name.data, 
                              contact_form.email.data,  
                              contact_form.body.data
                              )
        Contact.send_message(new_message)
        flash("Message Sent")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=contact_form)


# Message Fuctions
@app.route("/all-messages")
@login_required
def all_messages():
    message_posts = Message.query.all()
    return render_template("messages.html", posts=message_posts)


@app.route("/get-message-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def get_message_post(post_id):
    comment_form = CommentForm()
    requested_post = Message.query.get(post_id)
    message_comments = MessageComment.query.all()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login to submit a comment.")
            return redirect(url_for("login"))
        new_comment = MessageComment(
            author_id=current_user.id,
            message_post_id=post_id,
            message_text=comment_form.body.data,
            date=date.today().strftime("%B %d, %Y")
            )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_message_post", post_id=post_id))    
    return render_template("message-post.html", post=requested_post, form=comment_form, comments=message_comments)


@app.route("/create-message-post", methods=["GET", "POST"])
@login_required
def create_message_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Message(
            title=form.title.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("all_messages"))
    return render_template("make-message-post.html", form=form)


@app.route("/edit-message-post/<int:post_id>")
@login_required
def edit_message_post(post_id):
    post = Message.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.text.data
        db.session.commit()
        return redirect(url_for("get_message_post", post_id=post.id))
    return render_template("make-message-post.html", form=edit_form)


@app.route("/delete-message-post/<int:post_id>")
@login_required
def delete_message_post(post_id):
    post_to_delete = Message.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('all_messages'))


@app.route("/delete-message-comment/<int:comment_id>")
@login_required
def delete_message_comment(comment_id):
    comment_to_delete = MessageComment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('get_message_post', post_id=comment_to_delete.message_post_id))


# Blog Functions
@app.route("/all-blog-posts", methods=["GET", "POST"])
def all_blog_posts():
    blog_posts = BlogPost.query.all()
    return render_template("blog.html", posts=blog_posts)


@app.route("/get-blog-post/<int:post_id>", methods=["GET", "POST"])
def get_blog_post(post_id):
    comment_form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    blog_comments = BlogComment.query.all()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login to submit a comment.")
            return redirect(url_for("login"))
        new_comment = BlogComment(
            author_id=current_user.id,
            blog_post_id=post_id,
            blog_text=comment_form.body.data,
            date=date.today().strftime("%B %d, %Y")
            )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_blog_post", post_id=post_id))    
    return render_template("blog-post.html", post=requested_post, form=comment_form, comments=blog_comments)


@app.route("/create-blog-post", methods=["GET", "POST"])
@login_required
@admin_only
def create_blog_post():
    form = CreateBlogPost()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.blog_title.data,
            body=form.blog_text.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("all_blog_posts"))
    return render_template("make-blog-post.html", form=form)


@app.route("/edit-blog-post/<int:post_id>")
@login_required
@admin_only
def edit_blog_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreateBlogPost(
        blog_title=post.title,
        img_url=post.img_url,
        author=post.author,
        blog_text=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.blog_title.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.blog_text.data
        db.session.commit()
        return redirect(url_for("get_blog_post", post_id=post.id))
    return render_template("make-blog-post.html", form=edit_form)


@app.route("/delete-blog-post/<int:post_id>")
@login_required
@admin_only
def delete_blog_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('all_blog_posts'))


@app.route("/delete-blog-comment/<int:comment_id>")
@login_required
def delete_blog_comment(comment_id):
    comment_to_delete = BlogComment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('get_blog_post', post_id=comment_to_delete.blog_post_id))
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)