import datetime
import pytest

from lutabrawar import app
from lutabrawar.models import Death
from lutabrawar.filters import (format_date, url_for_char, 
    death_count, grouped_by)


@pytest.fixture
def deaths():
    A, B = app.config['GUILD_A'], app.config['GUILD_B']
    return [
        Death(guild=B),
        Death(guild=A),
        Death(guild=A),
        Death(guild=A),
        Death(guild=B),
        Death(guild=B),
        Death(guild=A),
    ]


def test_format_date():
    dt = datetime.datetime(2019, 12, 1, 10, 0, 0)
    assert 'Sunday, 01 Dec' == format_date(dt)


def test_url_for_char():
    expected = ('https://www.tibia.com/community/'
                '?subtopic=characters&amp;name=Nattank+Fazendo+Historia')
    assert expected == url_for_char('Nattank Fazendo Historia')
    assert expected == url_for_char('Nattank+Fazendo+Historia')


def test_death_score(deaths):
    assert (4, 3) == death_count(deaths)


def test_groupedby(deaths):
    A, B = app.config['GUILD_A'], app.config['GUILD_B']
    expected = [
        (B, [deaths[0]]),
        (A, deaths[1:4]),
        (B, deaths[4:6]),
        (A, [deaths[6]]),
    ]
    assert expected == grouped_by(deaths, 'guild')
