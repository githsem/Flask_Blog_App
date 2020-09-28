from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#Kullanici Kayit Formu
class RegisterForm(Form):
    name = StringField("Isim Soyisim", validators=[validators.length(min=4, max=25)])
    username = StringField("Kullanici Adi", validators=[validators.length(min=5, max=35)])
    email = StringField("Email Adresi", validators=[validators.Email(message="Lutfen Gecerli Bir Email Adresi Giriniz...")])
    password = PasswordField("Parola : ", validators=[
        validators.data_required(message="Lutfen Bir Parola Belirleyiniz..."),
        validators.equal_to(fieldname = "confirm", message = "Parolaniz Uyusmuyor...")
    ])
    confirm = PasswordField("Parola Dogrula")

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

#Kayit Olma
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        return redirect(url_for("index"))
    else:    
        return render_template("register.html",form = form)


if __name__ == "__main__":
    app.run(debug=True)