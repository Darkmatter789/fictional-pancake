from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps
from forms import EmailForm
from contact import Contact


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/about")
def about_us():
    return render_template("about.html")

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

@app.route("/messages")
def messages():
    return render_template("messages.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

if __name__ == "__main__":
    app.run(debug=True)