#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint

from flask import Flask, render_template, request, redirect, url_for

from data import *

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
version = [{'id': randint(1, 100000000)}]


@app.route("/")
def main():
    topics = get_topics()
    categories = get_categories()
    count_of_topic_in_cat(categories, topics)
    # build_html()
    return render_template('index.html', topics=topics, categories=categories, versions=version)


@app.route("/god")
def editor_mode():
    topics = get_topics()
    categories = get_categories()
    return render_template('god.html', topics=topics, categories=categories)


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
    icon = request.form['Icon']
    update_category(id, title, icon)
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
