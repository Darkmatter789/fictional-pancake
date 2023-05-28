from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, ValidationError
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[URL()])
    body = CKEditorField("Post Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CreateBlogPost(FlaskForm):
    blog_title = StringField("Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[URL()])
    blog_text = CKEditorField("Content", validators=[DataRequired()], render_kw={"style": "height: 250px"})
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField("First and Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Join")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class EmailForm(FlaskForm):

    def is_email(form, email):
        if "@" not in email.data or "." not in email.data:
            raise ValidationError("That is not a valid email address")
        

    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()], render_kw={"style": "height: 250px"})
    submit = SubmitField("Send")
