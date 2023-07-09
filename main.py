from flask import Flask, render_template, redirect, url_for, flash, abort, send_file
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from forms import EmailForm, RegisterForm, LoginForm, CreateBlogPost, CommentForm, CreatePostForm, DevotionalForm, NewsForm, WordForm, UserSearchForm, NewPasswordForm
from contact import Contact
from dotenv import load_dotenv
from boto3 import Session
from PIL import Image
import imageio
import skimage.transform as sk
import numpy as np
import os


app = Flask(__name__)


load_dotenv()


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///RCA-Users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def upload_file_to_s3():
    session = Session()
    aws_access_key_id = os.environ.get('AWS_ACCESS_ID')
    aws_secret_access_key = os.environ.get('AWS_ACCESS_SECRET')
    aws_region = os.environ.get('AWS_REGION')
    s3_bucket = 'rca-users'
    s3_file_path = "User-db/RCA-Users.db"
    local_file_path = "instance/RCA-Users.db"
    s3_client = session.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
    s3_client.upload_file(local_file_path, s3_bucket, s3_file_path)
   

def upload_img(img_obj):
    filename = secure_filename(img_obj.filename)
    path = "./static/uploads/" + filename
    img_obj.save((path))
    image = imageio.imread(path).astype(np.uint8)
    resized_image = sk.resize(image, (400, 600))
    pillow_image = Image.fromarray((resized_image * 255).astype(np.uint8))
    pillow_image.save(path)
    

def delete_img(img_filename):
    file_path = os.path.join('./static/uploads', img_filename)
    if os.path.exists(file_path):
        os.remove(file_path)


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
    img_upload = db.Column(db.String(250), nullable=False)
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
    img_upload = db.Column(db.String(250), nullable=False)
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


class DevotionalPost(db.Model):
    __tablename__ = "daily_devotional"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    img_upload = db.Column(db.String(250), nullable=False)


class NewsPost(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    news_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)


class WordPost(db.Model):
    __tablename__ = "word"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
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


# Checks uploaded img files and compares them to database filenames for association. Deletes img file if no association to post.
def img_association_check():
    blog_img_files = [entry.img_upload for entry in BlogPost.query.all()]
    message_img_files = [entry.img_upload for entry in Message.query.all()]
    devo_img_files = [entry.img_upload for entry in DevotionalPost.query.all()]
    for file in os.listdir('./static/uploads/'):
        if file not in blog_img_files and file not in message_img_files and file not in devo_img_files:
            delete_img(file)


# Homepage
@app.route("/", methods=["GET", "POST"])
def home():
    todays_date = str(date.today())
    devotional = DevotionalPost.query.all()
    news = NewsPost.query.all()
    word = WordPost.query.get(1)
    return render_template("index.html", devotional_posts=devotional, news=news, word=word, todays_date=todays_date)


# Dashboard for editing homepage ("index.html")
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
@admin_only
def dashboard():
    devotionals = DevotionalPost.query.all()
    devotional_form = DevotionalForm()
    news_form = NewsForm()
    word_form = WordForm()
    if devotional_form.validate_on_submit():
        devotional_post = DevotionalPost(
            title=devotional_form.title.data,
            img_url=devotional_form.img_url.data,
            text=devotional_form.text.data,
            date=devotional_form.launch_date.data,
            img_upload=devotional_form.img_upload.data.filename
        )
        if devotional_form.img_upload.data:
            upload_img(devotional_form.img_upload.data)
        db.session.add(devotional_post)
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("dashboard"))
    if news_form.validate_on_submit():
        news_post = NewsPost(
            news_text=news_form.body.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(news_post)
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("dashboard"))
    if word_form.validate_on_submit():
        word_post = WordPost(
            body=word_form.word_body.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(word_post)
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("dashboard"))
    return render_template("dashboard.html", dev_form=devotional_form, news_form=news_form, word_form=word_form, all_devs=devotionals)


@app.route("/all-devotionals", methods=["GET", "POST"])
@login_required
@admin_only
def all_devotionals():
    all_posts = DevotionalPost.query.all()
    return render_template("devotionals.html", posts=all_posts)


@app.route("/edit-devotional/<int:devo_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_devotional(devo_id):
    devotionals = DevotionalPost.query.all()
    news_form = NewsForm()
    word_form = WordForm()
    devo_to_edit = DevotionalPost.query.get(devo_id)
    edit_form = DevotionalForm(
        title=devo_to_edit.title,
        img_url=devo_to_edit.img_url,
        text=devo_to_edit.text,
        img_upload=devo_to_edit.img_upload
    )
    if edit_form.validate_on_submit():
        devo_to_edit.title=edit_form.title.data
        devo_to_edit.img_url=edit_form.img_url.data
        devo_to_edit.text=edit_form.text.data
        devo_to_edit.date=edit_form.launch_date.data
        devo_to_edit.img_upload=edit_form.img_upload.data.filename
        upload_img(edit_form.img_upload.data)
        db.session.commit()
        img_association_check()
        upload_file_to_s3()
        return redirect(url_for("all_devotionals"))
    return render_template("dashboard.html", dev_form=edit_form, news_form=news_form, word_form=word_form, all_devs=devotionals)


@app.route("/delete-devotional/<int:devo_id>")
@login_required
@admin_only
def delete_devotional(devo_id):
    devo_to_delete = DevotionalPost.query.get(devo_id)
    if devo_to_delete.img_upload:
        delete_img(devo_to_delete.img_upload)
    db.session.delete(devo_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for("all_devotionals"))


@app.route("/edit-news-post/<int:news_id>")
@login_required
@admin_only
def edit_news_post(news_id):
    devotionals = DevotionalPost.query.all()
    devotional_form = DevotionalForm()
    word_form = WordForm()
    news_to_edit = NewsPost.query.get(news_id)
    edit_form = NewsForm(
        body=news_to_edit.news_text
    )
    if edit_form.validate_on_submit():
        news_to_edit.news_text=edit_form.body.data
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("home"))
    return render_template("dashboard.html", dev_form=devotional_form, news_form=edit_form, word_form=word_form, all_devs=devotionals)


@app.route("/delete-news-post/<int:news_id>")
@login_required
@admin_only
def delete_news_post(news_id):
    post_to_delete = NewsPost.query.get(news_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for('home'))


@app.route("/edit-word-post/<int:word_id>")
@login_required
@admin_only
def edit_word_post(word_id):
    devotionals = DevotionalPost.query.all()
    devotional_form = DevotionalForm()
    news_form = NewsForm()
    word_to_edit = WordPost.query.get(word_id)
    edit_form = WordForm(
        word_body=word_to_edit.body
    )
    if edit_form.validate_on_submit():
        word_to_edit.body=edit_form.word_body.data
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("home"))
    return render_template("dashboard.html", dev_form=devotional_form, news_form=news_form, word_form=edit_form, all_devs=devotionals)


@app.route("/delete-word-post/<int:word_id>")
@login_required
@admin_only
def delete_word_post(word_id):
    post_to_delete = WordPost.query.get(word_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for('home'))


@app.route("/users")
@login_required
@admin_only
def users():
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/delete-user/<int:user_id>")
@login_required
@admin_only
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("users"))


@app.route("/view-images")
@login_required
@admin_only
def view_images():
    images = os.listdir('./static/uploads/')
    return render_template("images.html", images=images)


@app.route("/delete-image/<filename>")
@login_required
@admin_only
def delete_image(filename):
    delete_img(filename)
    return redirect(url_for("view_images"))


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
            upload_file_to_s3()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=reg_form)


@app.route("/reset-request", methods=["GET", "POST"])
def reset_request():
    all_users = {user.email:user.id for user in User.query.all()}
    request_form = UserSearchForm()
    if request_form.validate_on_submit():
        if request_form.email.data in all_users:
            verified_user_id = all_users[f"{request_form.email.data}"]
            verified_user = User.query.get(verified_user_id)
            Contact.send_reset_link(verified_user.email, verified_user.id)
            flash("A reset link has been sent to the email address. Please check your email.")
            return redirect(url_for("reset_request"))
        else:
            flash("The email address entered is not a registered user. Please register and login.")
    return render_template("reset-request.html", form=request_form)


@app.route("/reset/<int:user_id>", methods=["GET", "POST"])
def reset_password(user_id):
    user = User.query.get(user_id)
    form = NewPasswordForm()
    if form.validate_on_submit():
        if form.pwd.data == form.pwd_verified.data:
            user.password = generate_password_hash(form.pwd.data, 'pbkdf2:sha256', 8)
            db.session.commit()
            flash("Password reset successful. Please login")
            return redirect(url_for("login"))
        else:
            flash("The new passwords do not match. Please try again.")
            return redirect(url_for("reset_password", user_id=user_id))
    return render_template("reset.html", form=form)


# About page
@app.route("/about")
def about_us():
    return render_template("about.html")


# Contact page
@app.route("/contact")
def contact():
    contact_form = EmailForm()
    if contact_form.validate_on_submit():
        new_message = Contact(
            contact_form.name.data, 
            contact_form.email.data,  
            contact_form.body.data
            )
        Contact.send_message(new_message)
        flash("Message Sent")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=contact_form)


@app.route("/forms")
def forms():
    forms = os.listdir('./static/forms/')
    return render_template("forms.html", forms=forms)


@app.route("/download_pdf/<filename>")
def download_pdf(filename):
    file_path = './static/forms/'
    file = os.path.join(file_path, filename)
    return send_file(file, as_attachment=True)


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
        upload_file_to_s3()
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
            img_upload=form.img_upload.data.filename,
            date=date.today().strftime("%B %d, %Y")
        )
        if form.img_upload.data:
            upload_img(form.img_upload.data)
        db.session.add(new_post)
        db.session.commit()
        upload_file_to_s3()
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
        body=post.body,
        img_upload=post.img_upload
    )
    if edit_form.validate_on_submit():
        post.title=edit_form.title.data
        post.img_url=edit_form.img_url.data
        post.author=edit_form.author.data
        post.body=edit_form.text.data
        post.img_upload=edit_form.data.filename
        upload_img(edit_form.img_upload.data)
        db.session.commit()
        img_association_check()
        upload_file_to_s3()
        return redirect(url_for("get_message_post", post_id=post.id))
    return render_template("make-message-post.html", form=edit_form)


@app.route("/delete-message-post/<int:post_id>")
@login_required
def delete_message_post(post_id):
    post_to_delete = Message.query.get(post_id)
    if post_to_delete.img_upload:
        delete_img(post_to_delete.img_upload)
    db.session.delete(post_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for('all_messages'))


@app.route("/delete-message-comment/<int:comment_id>")
@login_required
def delete_message_comment(comment_id):
    comment_to_delete = MessageComment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    upload_file_to_s3()
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
        upload_file_to_s3()
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
            img_upload=form.img_upload.data.filename,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        if form.img_upload.data:
            upload_img(form.img_upload.data)
        db.session.add(new_post)
        db.session.commit()
        upload_file_to_s3()
        return redirect(url_for("all_blog_posts"))
    return render_template("make-blog-post.html", form=form)


@app.route("/edit-blog-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_blog_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreateBlogPost(
        blog_title=post.title,
        img_url=post.img_url,
        img_upload=post.img_upload,
        blog_text=post.body
    )
    if edit_form.validate_on_submit():
        post.title=edit_form.blog_title.data
        post.img_url=edit_form.img_url.data
        post.body=edit_form.blog_text.data
        post.img_upload=edit_form.img_upload.data.filename
        upload_img(edit_form.img_upload.data)
        db.session.commit()
        img_association_check()
        upload_file_to_s3()
        return redirect(url_for("get_blog_post", post_id=post.id))
    return render_template("make-blog-post.html", form=edit_form)


@app.route("/delete-blog-post/<int:post_id>")
@login_required
@admin_only
def delete_blog_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    if post_to_delete.img_upload:
        delete_img(post_to_delete.img_upload)
    db.session.delete(post_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for('all_blog_posts'))


@app.route("/delete-blog-comment/<int:comment_id>")
@login_required
def delete_blog_comment(comment_id):
    comment_to_delete = BlogComment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    upload_file_to_s3()
    return redirect(url_for('get_blog_post', post_id=comment_to_delete.blog_post_id))
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)