#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import os
from random import randint

import flask
from flask import Flask, render_template, redirect, url_for, request

from data import get_season, reformat_text
from models.category import get_categories, Category, count_of_topic_in_cat
from models.domain import get_domains, Domain
from models.topic import get_topics, search_topics, Topic, index_topics_by_category
from verify import requires_auth

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
    tasks = [get_topics(), get_categories(), get_season()]
    async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
    topics = async_values[0]
    categories = async_values[1]
    tech = [async_values[2]]
    count_of_topic_in_cat(categories, topics)
    index_topics_by_category(topics)
    return render_template('index.html', topics=topics, categories=categories, versions=version,
                           messages=messages, tech=tech)


@app.route("/god")
@requires_auth
def editor_mode():
    # Async gathering of data
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    tasks = [get_topics(), get_categories(), get_domains()]
    async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
    topics = async_values[0]
    categories = async_values[1]
    domains = async_values[2]
    return render_template('god.html', topics=topics, categories=categories, domains=domains)


# TOPICS
@app.route('/search', methods=['GET'])
def search():
    search_request = reformat_text(request.args['search'])
    search_results = search_topics(search_request)
    hosts = [flask.request.host_url]
    return render_template("search_results.html", results=search_results, hosts=hosts,
                           requests=[{'text': search_request, 'count': len(search_results)}], versions=version)


@app.route('/edit_topic', methods=['POST'])
def edit_topic():
    title = request.form['Title']
    link = request.form['URL']
    category_id = request.form['Categories']
    topic_id = request.form['id']
    Topic(topic_id=topic_id, name=title, link=link, category_id=category_id).update_topic()
    return redirect("/god")


@app.route('/delete_topic/<topic_id>')
def delete_topic(topic_id):
    Topic.remove_topic(int(topic_id))
    return redirect("/god")


@app.route('/add_topic', methods=['POST'])
def add_topic():
    title = request.form['Title']
    link = request.form['URL']
    category = request.form['Categories']
    topic = Topic(name=title, link=link, category_id=category)
    status = topic.create_topic()
    return redirect(url_for('.main', messages=status))


# CATEGORIES
@app.route('/edit_category', methods=['POST'])
def edit_category():
    title = request.form['Title']
    category_id = request.form['id']
    icon = request.form['Icon']
    Category(category_id=category_id, name=title, icon=icon).update_category()
    return redirect(url_for('editor_mode'))


@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    Category.remove_category(int(category_id))
    return redirect("/god")


@app.route('/add_category', methods=['POST'])
def add_category():
    title = request.form['Title']
    icon = request.form['Icon']
    Category(name=title, icon=icon).create_category()
    return redirect("/god")


# DOMAINS
@app.route('/edit_domain', methods=['POST'])
def edit_domain():
    old_domain = request.form['OldDomain']
    new_domain = request.form['NewDomain']
    Domain(name=old_domain).update_domain(new_domain=new_domain)
    return redirect(url_for('editor_mode'))


@app.route('/delete_domain/<domain>')
def delete_domain(domain):
    Domain(name=domain).remove_domain()
    return redirect("/god")


@app.route('/add_domain', methods=['POST'])
def add_domain():
    domain = request.form['Domain']
    Domain(name=domain).create_domain()
    return redirect("/god")


# ERRORS
@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return render_template('404.html', title='404'), 404


@app.errorhandler(500)
def server_error(error):
    print(error)
    return render_template('500.html', title='500'), 500


if __name__ == "__main__":
    app.run()
