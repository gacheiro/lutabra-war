from itertools import groupby
from jinja2 import Markup

from lutabrawar import app
from lutabrawar.scraping import char_url


@app.template_filter('format_date')
def format_date(date):
    """Formats date as in Saturday, 30 Nov."""
    return Markup.escape(date.strftime('%A, %d %b'))


@app.template_filter('url_for_char')
def url_for_char(char_name):
    """Returns a url for the character's page."""
    char_name = '+'.join(name for name in char_name.split())
    url = char_url(char_name)
    return Markup.escape(url)


@app.template_filter('link_to_char')
def link_to_char(death):
    """Returns a formatted (bold) link to 
    the tibia community character's page.

    This filter is used with the jinja2 map and join filters to render
    a nice list of names.

    Ex: [752] Rubini, [751] Gordini, ...
    """
    url = url_for_char(death.char_name)
    name = Markup.escape(death.char_name)
    return Markup(
        '<strong>'
        f'<a href={url} target="_blank">[{death.level}] {name}</a>'
        '</strong>'
    )


@app.template_filter('death_count')
def death_count(deaths):
    """Returns death count by each guild."""
    deaths_a, deaths_b = 0, 0
    for death in deaths:
        if death.guild == app.config['GUILD_A']:
            deaths_a += 1
        else:
            deaths_b += 1
    return deaths_a, deaths_b


@app.template_filter('grouped_by')
def grouped_by(items, attr):
    """Groups successives items with the same attr together."""
    groups = groupby(items, lambda x: getattr(x, attr))
    # parse the result into a list of tuples (grouper, grouped items),
    # so it can be iterated more than once
    return [(grouper, list(items)) for grouper, items in groups]
