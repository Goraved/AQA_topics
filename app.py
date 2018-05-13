#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for

from data import *

app = Flask(__name__)


@app.route("/")
def main():
    topics = get_topics()
    header_topics = get_header_topics()
    categories = get_categories(False)
    list_categories = get_categories_list()
    # build_html()
    return render_template('index.html', header_topics=header_topics, topics=topics, categories=categories,
                           list_categories=list_categories)


@app.route("/god")
def editor_mode():
    topics = get_topics()
    categories = get_categories(True)
    list_categories = get_categories_list()
    return render_template('god.html', topics=topics, categories=categories, list_categories=list_categories)


@app.route('/edit_topic', methods=['POST'])
def edit_topic():
    title = request.form['Title']
    link = request.form['URL']
    category = request.form['Categories']
    id = request.form['id']
    update_topic(id, title, link, category)
    return redirect("/god")


@app.route('/delete_topic/<topic_id>')
def delete_topic(topic_id):
    remove_topic(topic_id)
    return redirect("/god")


@app.route('/add_topic', methods=['POST'])
def add_topic():
    title = request.form['Title']
    link = request.form['URL']
    category = request.form['Categories']
    create_topic(title, link, category)
    return redirect("/")


@app.route('/edit_category', methods=['POST'])
def edit_category():
    title = request.form['Title']
    id = request.form['id']
    update_category(id, title)
    return redirect(url_for('editor_mode'))


@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    remove_category(category_id)
    return redirect("/god")


@app.route('/add_category', methods=['POST'])
def add_category():
    title = request.form['Title']
    create_category(title)
    return redirect("/god")


if __name__ == "__main__":
    app.run()
