# AQA Topics

A knowledge-sharing platform for Automation QA engineers. This project aggregates QA topics, tutorials, and resources in
one organized location.

## Overview

AQA Topics is a web application that helps QA engineers find and share valuable resources. The platform organizes
content by categories, making it easy to discover relevant information.

## Features

- **Topic Management**: Browse, add, edit, and delete QA-related topics
- **Category Organization**: Topics grouped by categories with icons
- **Search Functionality**: Find specific topics quickly
- **Admin Panel**: Protected editor mode for content management
- **Responsive Design**: Works on various devices

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Data Storage**: Database (implementation details abstracted)
- **Authentication**: Basic auth for admin features
- **Deployment**: Hosted on Vercel (previously Heroku)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aqa-topics.git
   cd aqa-topics
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # For development
   export FLASK_APP=index.py
   export FLASK_ENV=development
   # Authentication credentials (for admin access)
   export AUTH_USERNAME=admin
   export AUTH_PASSWORD=yourpassword
   ```

5. **Run the application**
   ```bash
   flask run
   ```

## Usage

- **Browse Topics**: Visit the homepage to see all topics organized by categories
- **Search**: Use the search feature to find specific topics
- **Add Content**: Submit new topics through the add topic form
- **Admin Access**: Visit `/god` route with proper authentication to manage all content

## Deployment

The application is deployed at:

- [https://aqa-topics.vercel.app/](https://aqa-topics.vercel.app/)

## Project Structure

- `index.py`: Main application file with routes and request handlers
- `templates/`: HTML templates for the web pages
- Models for Topic, Category, and Domain entities
- Async handlers for data retrieval

