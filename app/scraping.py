import re
import datetime
import requests

TIBIA_COMMUNITY_URL = 'https://www.tibia.com/community/'

"""
Guild member pattern. Finds members in guild page html. Ex:

&name=Alice+Spectre">Alice&#160;Spectre</A></TD>
<TD>Master Sorcerer</TD>
<TD>288</TD>
<TD>Dec&#160;28&#160;2018</TD>

Please use https://regex101.com/ to test.
"""
guid_member_pattern = (r'&name=(?P<char_name>[\w\+%\d]+)'
                       r'(.)+\s?<TD>'
                       r'(?P<vocation>[\w\s]+)</TD>\s?<TD>'
                       r'(?P<level>[\d]+)</TD>')


"""
Death pattern. Finds death entries in character page html. Ex:

valign="top">Nov&#160;26&#160;2019,&#160;21:36:23&#160;CET</td>
<td>Died at Level 1099 by an energetic book.<br />

Please use https://regex101.com/ to test.
"""
death_pattern = (r'top">(?P<m>[\w]+)+&#160;(?P<d>\d{2})&#160;(?P<y>\d{4}),&#160;(?P<t>\d{2}:\d{2}:\d{2})&#160;CET(.*?)'
                 r'at Level\s(?P<level>[\d]+)')


def char_url(char_name):
    char_name = '+'.join(char_name.split())
    return f'{TIBIA_COMMUNITY_URL}?subtopic=characters&name={char_name}'


def guild_url(guild_name):
    guild_name = '+'.join(guild_name.split())
    return f'{TIBIA_COMMUNITY_URL}?subtopic=guilds&page=view&GuildName={guild_name}'


def parse_date(death_match):
    month, day, year, time = (death_match.group('m'),
                              death_match.group('d'),
                              death_match.group('y'),
                              death_match.group('t'))
    date_str = f'{month} {day} {year}, {time}'
    return datetime.datetime.strptime(date_str, '%b %d %Y, %H:%M:%S')


def fetch_page(url):
    response = requests.get(url)
    assert 'does not exist' not in response.text, url
    return response.text


def find_guild_members(html):
    for m in re.finditer(guid_member_pattern, html):
        yield m


def find_deaths(html):
    for m in re.finditer(death_pattern, html):
        yield m


def guild_members(html):
    for member in find_guild_members(html):
        # transforms First+Last in First Last
        yield (' '.join(member.group('char_name').split('+')),
               member.group('vocation'),
               int(member.group('level')))


def char_deaths(html):
    for death in find_deaths(html):
        yield parse_date(death), int(death.group('level'))


def fetch_all(guilds, min_level, fetch=fetch_page):
    for guild_name in guilds:
        guild_page = fetch(guild_url(guild_name))
        for char_name, voc, level in guild_members(guild_page):
            if level < min_level:
                continue
            char_page = fetch(char_url(char_name))
            for date, level in char_deaths(char_page):
                yield {
                        'char_name': char_name,
                        'level': level,
                        'vocation': voc,
                        'datetime': date,
                        'guild': guild_name,
                    }
