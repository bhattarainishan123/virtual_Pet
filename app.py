from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)
@app.route("/")
def pet():
    return render_template("pet.html", name="Blaze", emoji="🐉", species="Dragon", level=2, hunger=40, happiness=28, energy=10)


@app.route("/feed", methods=["POST"])
def feed():
    return redirect(url_for("pet"))


@app.route("/play", methods=["POST"])
def play():
    return redirect(url_for("pet"))


@app.route("/sleep", methods=["POST"])
def sleep():
    return redirect(url_for("pet"))