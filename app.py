from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def pet():
    return render_template("pet.html", name="Blaze", emoji="🐉", species="Dragon", level=2, hunger=40, happiness=28, energy=10)