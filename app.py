from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
fake_pet = {
    "name": "Blaze",
    "emoji": "🐉",
    "species": "Dragon",
    "level": 2,
    "xp": 46,
    "hunger": 40,
    "happiness": 28,
    "energy": 10,
}
@app.route("/")
def pet():
    return render_template("pet.html", pet=fake_pet)


@app.route("/feed", methods=["POST"])
def feed():
    return redirect(url_for("pet"))


@app.route("/play", methods=["POST"])
def play():
    return redirect(url_for("pet"))


@app.route("/sleep", methods=["POST"])
def sleep():
    return redirect(url_for("pet"))

@app.route("/adopt", methods=["GET", "POST"])
def adopt():
    species = [
        {"name": "Cat", "emoji": "🐱", "trait": "Independent"},
        {"name": "Dog", "emoji": "🐶", "trait": "Loves attention"},
        {"name": "Bunny", "emoji": "🐰", "trait": "Always snacking"},
        {"name": "Dragon", "emoji": "🐉", "trait": "Earns extra XP"},
        {"name": "Unicorn", "emoji": "🦄", "trait": "Levels up fastest"},
    ]
    if request.method == "POST":
        chosen = request.form["species"]
        name = request.form["pet_name"]
        fake_pet["name"] = name
        fake_pet["species"] = chosen
        return redirect(url_for("pet"))
    return render_template("adopt.html", species=species)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("pet"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect(url_for("adopt"))
    return render_template("signup.html")
