from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, EmailField, FileField
from wtforms.validators import DataRequired, URL, ValidationError, Optional
from flask_ckeditor import CKEditorField


def is_email(form, email):
        if "@" not in email.data or "." not in email.data:
            raise ValidationError("That is not a valid email address")
        

class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[Optional(), URL()])
    img_upload = FileField("Upload an Image", validators=[Optional()])
    body = CKEditorField("Post Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CreateBlogPost(FlaskForm):
    blog_title = StringField("Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[Optional(), URL()])
    img_upload = FileField("Upload an Image", validators=[Optional()])
    blog_text = CKEditorField("Content", validators=[DataRequired()], render_kw={"style": "height: 250px"})
    preview = SubmitField("Preview Post")
    submit = SubmitField("Submit Post")
    

class RegisterForm(FlaskForm):        
    name = StringField("First and Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), is_email])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Join")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), is_email])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class DevotionalForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[Optional(), URL()])
    img_upload = FileField("Upload an Image", validators=[Optional()])
    text = CKEditorField("Post Content", validators=[DataRequired()])
    launch_date = DateField("Launch Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NewsForm(FlaskForm):
    body = CKEditorField("News Post", validators=[DataRequired()])
    submit = SubmitField("Submit")


class WordForm(FlaskForm):
    word_body = CKEditorField("Post Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EmailForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), is_email])
    message = CKEditorField("Message", validators=[DataRequired()], render_kw={"style": "height: 250px"})
    submit = SubmitField("Send")


class UserSearchForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), is_email])
    submit = SubmitField("Send Email")


class NewPasswordForm(FlaskForm):
    pwd = PasswordField("New Password", validators=[DataRequired()])
    pwd_verified = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Submit")