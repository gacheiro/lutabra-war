import os
import datetime

from lutabrawar import app
from lutabrawar.models import Death
from lutabrawar.filters import format_date, link_to_char


def test_index(client, seed):
    rv = client.get('/')
    assert 200 == rv.status_code
    assert b'Rubini' in rv.data
    assert b'Nattank Fazendo Historia' in rv.data
    # ensure deaths are align left (Almighty Os)
    # and right (Skeletin Alliance)
    assert b'has-text-left' in rv.data
    assert b'has-text-right' in rv.data
    for death in Death.query.all():
        death_date = format_date(death.date)
        # ensure deaths are grouped by date
        assert death_date.encode() in rv.data
        # ensure links to characters are present
        assert link_to_char(death).encode() in rv.data
        # ensures sidebar (with links) is present
        assert f'href="#{death_date}"'.encode() in rv.data
    # ensures deaths are sorted desc by date
    assert rv.data.find(b'Nattank Fazendo Historia') < rv.data.find(b'Rubini')


def test_guild_names_on_index(client, config):
    # ensures guild names show up on page
    rv = client.get('/')
    assert config['GUILD_A'].encode() in rv.data
    assert config['GUILD_B'].encode() in rv.data
