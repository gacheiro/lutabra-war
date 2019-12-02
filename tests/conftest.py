import os
import datetime
import pytest


@pytest.fixture
def client():
    os.environ['FLASK_ENV'] = 'test'
    os.environ['APP_SETTINGS'] = 'config.DevelopmentConfig'
    from app import app, db
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def seed(client):
    from app.models import db, Death
    deaths = [
        {
            'char_name': 'Rubini',
            'level': 752,
            'vocation': 'Elite Knight',
            'guild': 'Almighty Os',
            'datetime': datetime.datetime(2019, 12, 1, 10, 0, 0),
        },
        {
            'char_name': 'Nattank Fazendo Historia',
            'level': 720,
            'vocation': 'Elite Knight',
            'guild': 'Skeletin Alliance',
            'datetime': datetime.datetime(2019, 12, 2, 10, 0, 0),
        }
    ]
    for death in deaths:
        db.session.add(Death(**death))
    db.session.commit()
