from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#Kullanici Kayit Formu
class RegisterForm(Form):
    name = StringField("Isim Soyisim", validators=[validators.length(min=4, max=25)])
    username = StringField("Kullanici Adi", validators=[validators.length(min=5, max=35)])
    name = StringField("Isim Soyisim", validators=[validators.length(min=4, max=25)])


app = Flask(__name__)
app.config["MySQL_HOST"] = "localhost"
app.config["MySQL_USER"] = "root"
app.config["MySQL_PASSWORD"] = ""
app.config["MySQL_DB"] = "ybblog"
app.config["MySQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    articles = [
        {"id":1,"title":"Deneme1","content":"Deneme1 Icerik"},
        {"id":2,"title":"Deneme2","content":"Deneme2 Icerik"},
        {"id":3,"title":"Deneme2","content":"Deneme2 Icerik"}
    ]
    return render_template("index.html",articles = articles)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article/<string:id>")
def detail(id):
    return "Article Id: " + id    

if __name__ == "__main__":
    app.run(debug=True)