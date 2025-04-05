#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Main application file for AQA Topics, a knowledge-sharing platform for Automation QA engineers.
This file contains the Flask application setup, route definitions, and error handlers.
"""

import asyncio
import logging
import os
from random import randint

import flask
from flask import Flask, render_template, redirect, url_for, request
from flask_compress import Compress  # Add compression

from data import get_season, reformat_text
from models.category import get_categories, Category, count_of_topic_in_cat
from models.domain import get_domains, Domain
from models.topic import get_topics, search_topics, Topic, index_topics_by_category
from verify import requires_auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")

# Enable Flask compression for faster page loading
compress = Compress()
compress.init_app(app)

# Set application version from environment variable or generate a random version
try:
    version = [{"id": os.environ["HEROKU_RELEASE_VERSION"]}]
except KeyError:
    version = [{"id": randint(1, 100000000)}]


@app.route("/")
def main():
    """
    Main route for the application. Renders the homepage with topics, categories, and other information.
    """
    try:
        messages = [{"text": request.args["messages"]}]
    except KeyError:
        messages = [{"text": ""}]

    try:
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
        ioloop.close()  # Properly close the event loop
    except Exception as e:
        logger.error(f"Error in main route: {e}")
        return render_template("500.html", title="500"), 500

    return render_template(
        "index.html",
        topics=topics,
        categories=categories,
        versions=version,
        messages=messages,
        tech=tech,
    )


@app.route("/god")
@requires_auth
def editor_mode():
    """
    Route for admin/editor mode. Renders the editor page with topics, categories, and domains.
    Requires authentication.
    """
    try:
        # Async gathering of data
        ioloop = asyncio.new_event_loop()
        asyncio.set_event_loop(ioloop)
        tasks = [get_topics(), get_categories(), get_domains()]
        async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
        topics = async_values[0]
        categories = async_values[1]
        domains = async_values[2]
        ioloop.close()  # Properly close the event loop
    except Exception as e:
        logger.error(f"Error in editor_mode route: {e}")
        return render_template("500.html", title="500"), 500

    return render_template(
        "god.html", topics=topics, categories=categories, domains=domains
    )


# TOPICS
@app.route("/search", methods=["GET"])
def search():
    """
    Route for searching topics. Renders the search results page.
    """
    try:
        search_request = reformat_text(request.args["search"])
        search_results = search_topics(search_request)
        hosts = [flask.request.host_url]
    except Exception as e:
        logger.error(f"Error in search route: {e}")
        return render_template("500.html", title="500"), 500

    return render_template(
        "search_results.html",
        results=search_results,
        hosts=hosts,
        requests=[{"text": search_request, "count": len(search_results)}],
        versions=version,
    )


@app.route("/edit_topic", methods=["POST"])
@requires_auth
def edit_topic():
    """
    Route for editing a topic. Updates the topic with the provided data.
    Requires authentication.
    """
    try:
        title = request.form["Title"]
        link = request.form["URL"]
        category_id = request.form["Categories"]
        topic_id = request.form["id"]
        Topic(
            topic_id=topic_id, name=title, link=link, category_id=category_id
        ).update_topic()
    except Exception as e:
        logger.error(f"Error in edit_topic route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


@app.route("/delete_topic/<topic_id>")
@requires_auth
def delete_topic(topic_id):
    """
    Route for deleting a topic. Removes the topic with the given ID.
    Requires authentication.
    """
    try:
        Topic.remove_topic(int(topic_id))
    except Exception as e:
        logger.error(f"Error in delete_topic route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


@app.route("/add_topic", methods=["POST"])
def add_topic():
    """
    Route for adding a new topic. Creates a new topic with the provided data.
    """
    try:
        title = request.form["Title"]
        link = request.form["URL"]
        category = request.form["Categories"]
        topic = Topic(name=title, link=link, category_id=category)
        status = topic.create_topic()
    except Exception as e:
        logger.error(f"Error in add_topic route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect(url_for(".main", messages=status))


# CATEGORIES
@app.route("/edit_category", methods=["POST"])
@requires_auth
def edit_category():
    """
    Route for editing a category. Updates the category with the provided data.
    Requires authentication.
    """
    try:
        title = request.form["Title"]
        category_id = request.form["id"]
        icon = request.form["Icon"]
        Category(category_id=category_id, name=title, icon=icon).update_category()
    except Exception as e:
        logger.error(f"Error in edit_category route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect(url_for("editor_mode"))


@app.route("/delete_category/<category_id>")
@requires_auth
def delete_category(category_id):
    """
    Route for deleting a category. Removes the category with the given ID.
    Requires authentication.
    """
    try:
        Category.remove_category(int(category_id))
    except Exception as e:
        logger.error(f"Error in delete_category route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


@app.route("/add_category", methods=["POST"])
@requires_auth
def add_category():
    """
    Route for adding a new category. Creates a new category with the provided data.
    Requires authentication.
    """
    try:
        title = request.form["Title"]
        icon = request.form["Icon"]
        Category(name=title, icon=icon).create_category()
    except Exception as e:
        logger.error(f"Error in add_category route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


# DOMAINS
@app.route("/edit_domain", methods=["POST"])
@requires_auth
def edit_domain():
    """
    Route for editing a domain. Updates the domain with the provided data.
    Requires authentication.
    """
    try:
        old_domain = request.form["OldDomain"]
        new_domain = request.form["NewDomain"]
        Domain(name=old_domain).update_domain(new_domain=new_domain)
    except Exception as e:
        logger.error(f"Error in edit_domain route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect(url_for("editor_mode"))


@app.route("/delete_domain/<domain>")
@requires_auth
def delete_domain(domain):
    """
    Route for deleting a domain. Removes the domain with the given name.
    Requires authentication.
    """
    try:
        Domain(name=domain).remove_domain()
    except Exception as e:
        logger.error(f"Error in delete_domain route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


@app.route("/add_domain", methods=["POST"])
@requires_auth
def add_domain():
    """
    Route for adding a new domain. Creates a new domain with the provided data.
    Requires authentication.
    """
    try:
        domain = request.form["Domain"]
        Domain(name=domain).create_domain()
    except Exception as e:
        logger.error(f"Error in add_domain route: {e}")
        return render_template("500.html", title="500"), 500

    return redirect("/god")


# ERRORS
@app.errorhandler(404)
def page_not_found(error):
    """
    Error handler for 404 Not Found. Renders the 404 error page.
    """
    logger.error(f"404 error: {error}")
    return render_template("404.html", title="404"), 404


@app.errorhandler(500)
def server_error(error):
    """
    Error handler for 500 Internal Server Error. Renders the 500 error page.
    """
    logger.error(f"500 error: {error}")
    return render_template("500.html", title="500"), 500


if __name__ == "__main__":
    app.run()
