from flask import Flask, Blueprint, session, redirect

lt = Blueprint("logout", __name__)

@lt.route("/logout")
def logout():
    del session["user_info"]
    return redirect("/login")