from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators


app = Flask(__name__)
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