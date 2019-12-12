import os
from itertools import groupby
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Markup

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from lutabrawar.models import Death
from lutabrawar.scraping import fetch_all
from lutabrawar.filters import grouped_by


@app.before_request
def before_request():
    """Forces https requests on production."""
    if not request.is_secure and app.env == 'production':
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


@app.route('/')
def index():
    query = Death.query.order_by(Death.datetime.desc()).all()
    return render_template('index.html', deathlist=query)


@app.cli.command('create-db')
def create_db():
    db.create_all()


@app.cli.command('update-db')
def update_db():
    print('Update start.')
    # deletes all death records
    db.session.query(Death).delete()
    # repopulates the db with new death records
    guilds = (app.config['GUILD_A'], app.config['GUILD_B'])
    min_level = app.config['MINIMUN_LEVEL']
    print(f"Fetching deaths of players level {min_level}+")
    for death in fetch_all(guilds, min_level):
        if app.config['DEBUG']:
            print(death)
        db.session.add(Death(**death))
    db.session.commit()
    print('Update done.')


@app.cli.command('stats-db')
def stats_db():
    print(Death.query.count())


@app.cli.command('drop-db')
def drop_db():
    db.drop_all()
