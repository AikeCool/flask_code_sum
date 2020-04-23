from flask import Flask, Blueprint, render_template

blue_index = Blueprint("index", __name__)

@blue_index.route("/index")
def index():
    return render_template("index.html")