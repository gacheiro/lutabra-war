import datetime
import pytest
from app.scraping import guild_members, char_deaths, fetch_all

# list of guild members in '_fixtures/guild.html'
os_members = [
    # char name, vocation, level
    ('Freire Lutabra Defender', 'Elite Knight', 1100),
    ('Rubini', 'Elite Knight', 752),
    ('Alice Spectre', 'Master Sorcerer', 288),
    ('Aury', 'Elite Knight', 355),
    ('Balothh', 'Master Sorcerer', 704),
    ('Diego Barral', 'Elder Druid', 381),
    # %27 is the character '
    ("Fen%27yx", 'Master Sorcerer', 502),
    ("Geniuz Under%27ground", 'Elite Knight', 407),
    ('Canneta Azull', 'Master Sorcerer', 21),  
    ('Lutabra Defenderr', 'Paladin', 8),
]

# list of deaths in '_fixtures/char.html'
freire_deaths = [
    # datetime(year, month, day, hour, min, sec), level
    (datetime.datetime(2019, 11, 26, 21, 36, 23), 1099),
    (datetime.datetime(2019, 11, 20, 23, 27, 43), 1095),
]


@pytest.fixture(scope='module')
def guild_page():
    with open('tests/_fixtures/guild.html') as page:
        return page.read()


@pytest.fixture(scope='module')
def char_page():
    with open('tests/_fixtures/char.html') as page:
        return page.read()


def test_guild_members(guild_page):
    members = guild_members(html=guild_page)
    assert os_members == list(members)


def test_char_deaths(char_page):
    deaths = char_deaths(html=char_page)
    assert freire_deaths == list(deaths)


def fetch(pages=[]):
    it = iter(pages)
    def _fetch(url):
        while True:
            return next(it)
    return _fetch


def test_fetch_all(guild_page, char_page):
    guilds = ['Almight Os']
    f = fetch([guild_page, char_page])
    deaths = list(fetch_all(guilds, min_level=1100, fetch=f))
    assert 2 == len(deaths)
    # ensures min_level filter is applied
    f = fetch([guild_page, char_page])
    deaths = list(fetch_all(guilds, min_level=1101, fetch=f))
    assert 0 == len(deaths)
