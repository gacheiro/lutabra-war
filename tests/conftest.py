import os
import datetime
import pytest

# app is created at import time, so we need to
# define the env here before any module imports it
os.environ['FLASK_ENV'] = 'test'
os.environ['APP_SETTINGS'] = 'config.TestingConfig'


@pytest.fixture
def client():
    from lutabrawar import app, db
    assert 'sqlite:///:memory:' == app.config['SQLALCHEMY_DATABASE_URI']
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def config():
    from lutabrawar import app
    return app.config
    

@pytest.fixture
def seed(client):
    from lutabrawar.models import db, Death
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
