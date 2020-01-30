#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint

from flask import Flask, render_template, redirect, url_for

from data import *
from verify import *

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
try:
    version = [{'id': os.environ['HEROKU_RELEASE_VERSION']}]
except:
    version = [{'id': randint(1, 100000000)}]


@app.route("/")
def main():
    try:
        messages = [{'text': request.args['messages']}]
    except KeyError:
        messages = [{'text': ''}]

    # Async gathering of data
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    tasks = [get_topics(), get_categories()]
    async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
    topics = async_values[0]
    categories = async_values[1]

    count_of_topic_in_cat(categories, topics)
    index_topics_by_category(topics)
    return render_template('index.html', topics=topics, categories=categories, versions=version,
                           messages=messages)


@app.route("/god")
@requires_auth
def editor_mode():
    # Async gathering of data
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    tasks = [get_topics(), get_categories()]
    async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
    topics = async_values[0]
    categories = async_values[1]
    return render_template('god.html', topics=topics, categories=categories)


@app.route('/search', methods=['GET'])
def search():
    search_request = reformat_text(request.args['search'])
    search_results = search_topics(search_request)
    return render_template("search_results.html", results=search_results,
                           requests=[{'text': search_request, 'count': len(search_results)}], versions=version)


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
    status = create_topic(title, link, category)
    return redirect(url_for('.main', messages=status))


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
    icon = request.form['Icon']
    create_category(title, icon)
    return redirect("/god")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', title='500'), 500


if __name__ == "__main__":
    app.run()
