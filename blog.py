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

#Makale Sayfasi
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles"
    result = cursor.execute(sorgu)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")    

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles WHERE author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    
    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
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

#Detay Sayfasi
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles WHERE id =%s"
    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html", article = article)
    else:
        return render_template("article.html")    

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

#Makale Ekleme
@app.route("/addarticle", methods = ["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()
        sorgu = "INSERT INTO articles(title, author, content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title, session["username"],content))

        mysql.connection.commit()
        cursor.close()

        flash("Makale Basariyla Eklendi...","success")
        return redirect(url_for("dashboard"))

    return render_template("addarticle.html", form = form)

#Makale Silme
@app.route("/delete/<string:id>")   
@login_required 
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles WHERE author = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "DELETE FROM articles WHERE id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("Boyle Bir Makale Yok veya Bu Isleme  Yetkiniz Yok","danger")    
        return redirect(url_for("index"))

#Makale Guncelleme
@app.route("/edit/<string:id>", methods =["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM articles WHERE and id = %s author = %s "
        result = cursor.execute(sorgu,(id,session["username"]))

        if result == 0:
            flash("Boyle Bir Makale Yok veya Bu Isleme  Yetkiniz Yok","danger")    
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()

            form.title.data = article["title"]
    else:
        pass


#Makale Form
class ArticleForm(Form):
    title = StringField("Makale Basligi", validators=[validators.length(min = 5, max = 100)])  
    content = TextAreaField("Makale Icerigi", validators=[validators.length(min = 10)])  

if __name__ == "__main__":
    app.run(debug=True)