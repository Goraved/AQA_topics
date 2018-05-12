from flask import Flask, render_template, request, redirect

from data import *

app = Flask(__name__)


@app.route("/")
def main():
    topics = get_topics()
    header_topics = get_header_topics()
    categories = get_categories()
    list_categories = get_categories_list()
    # build_html()
    return render_template('index.html', header_topics=header_topics, topics=topics, categories=categories,
                           list_categories=list_categories)


@app.route('/add_topic', methods=['POST'])
def my_form_post():
    title = request.form['Title']
    link = request.form['URL']
    category = request.form['Categories']
    create_topic(title, link, category)
    return redirect("/")


if __name__ == "__main__":
    app.run()
