import os
from itertools import groupby
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Markup

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from app.models import Death
from app.scraping import fetch_all


@app.route('/')
def index():
    query = Death.query.order_by(Death.datetime.desc()).all()
    # group deaths in the same day together
    deathlist = groupby(query, lambda d: d.date)
    return render_template('index.html', deathlist=deathlist)


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


@app.template_filter('format_date')
def format_date(date):
    """Formats date as: Saturday, 30 Nov"""
    return Markup.escape(date.strftime('%A, %d %b'))


@app.template_filter('url_for_char')
def url_for_char(char_name):
    char_name = '+'.join(name for name in char_name.split())
    char_url = ('https://www.tibia.com/community/'
                f'?subtopic=characters&name={char_name}')
    return Markup.escape(char_url)
