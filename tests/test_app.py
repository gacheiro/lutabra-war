import os
import datetime

from lutabrawar import app
from lutabrawar.models import Death
from lutabrawar.filters import format_date, url_for_char


def test_index(client, seed):
    rv = client.get('/')
    assert 200 == rv.status_code
    assert b'Rubini' in rv.data
    assert b'Nattank Fazendo Historia' in rv.data
    assert rv.data.count(b'Elite Knight') == 2
    # ensure deaths are align left (Almighty Os)
    # and right (Skeletin Alliance)
    assert b'has-text-left' in rv.data
    assert b'has-text-right' in rv.data
    for death in Death.query.all():
        death_date = format_date(death.date)
        # ensure deaths are grouped by date
        assert death_date.encode() in rv.data
        # ensure links to characters are present
        assert url_for_char(death.char_name).encode() in rv.data
        # ensures sidebar (with links) is present
        assert f'href="#{death_date}"'.encode() in rv.data
    # ensures deaths are sorted desc by date
    assert rv.data.find(b'Nattank Fazendo Historia') < rv.data.find(b'Rubini')
