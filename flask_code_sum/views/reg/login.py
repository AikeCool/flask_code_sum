from flask import Flask, Blueprint, render_template, redirect, request, session
import pymysql

lg = Blueprint("login", __name__)


@lg.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    # 获取用户名和密码
    username = request.form.get("username")
    pwd = request.form.get("password")
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "123456", "code_sum")
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from user where username=%s and password=%s"
    para = (username, pwd)
    # cursor.execute("select * from user where username=%s and password=%s", (username, pwd))
    cursor.execute(sql, para)
    ret = cursor.fetchone()
    cursor.close()
    db.close()
    if not ret:
        return render_template("login.html", error="用户名或密码错误")

    session["user_info"] = {
        "user_id": ret["id"],
        "username": ret["username"]
    }

    return redirect("/index")
