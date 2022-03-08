from flask import Flask, redirect, url_for, render_template, request
from search import initialize, run
import sys
from builtins import print

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/results", methods=['POST'])
def search():
    if request.method == "POST":
        query = request.form.items()
        term = ''
        for i, val in query:
            term = val
        urls, query_time = run(term, index_of_doc_to_tf, index_of_doc_to_tf_2grams, index_of_tokens_to_postings,
        index_of_two_grams, tokens_to_postings, two_grams_to_postings, doc_id_to_url)
        return render_template("results.html", query_term = term, sites = urls, query_time = query_time)

if __name__ == "__main__":
    index_of_doc_to_tf, index_of_doc_to_tf_2grams, index_of_tokens_to_postings, index_of_two_grams, tokens_to_postings, two_grams_to_postings, doc_id_to_url = initialize()
    app.run(debug=True)