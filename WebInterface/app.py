from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=['POST'])
def search():
    if request.method == "POST":
        query = request.form['nm']
        return redirect(url_for('result',name = user))

    
    
if __name__ == "__main__":
    app.run(debug=True)