from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def pet():
    return render_template("pet.html")