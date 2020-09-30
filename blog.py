from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


#Kullanici Giris Decorator'i
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu Sayfayi Goruntulemek Icin Lutfen Giris Yapiniz...","danger")    
            return redirect(url_for("login"))
    return decorated_function

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

class LoginForm(Form):
    username = StringField("Kullanici Adi")    
    password = PasswordField("Parola")

app = Flask(__name__)
app.secret_key = "ybblog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")    

#Kayit Olma
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()     
        sorgu = "Insert INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash("Basariyla Kayit Oldunuz...","success")
        return redirect(url_for("login"))

    else:    
        return render_template("register.html",form = form)

#Login Islemi
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(sorgu,(username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Basariyla Giris Yaptiniz...","success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanizi Yanlis Girdiniz...","danger")
                return redirect(url_for("login"))    

        else:
            flash("Boyle Bir Kullanici Bulunmuyor...","danger")
            return redirect(url_for("login"))


    return render_template("login.html",form = form)

#Logout Islemi
@app.route("/logout")    
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)