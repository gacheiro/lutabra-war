import re
import datetime
import requests

TIBIA_COMMUNITY_URL = 'https://www.tibia.com/community/?subtopic=characters&name='

guid_member_pattern = r'&name=(?P<char_name>[\w\+%\d]+)(.)+\s?<TD>(?P<vocation>[\w\s]+)</TD>\s?<TD>(?P<level>[\d]+)</TD>'
death_pattern = r'top\">(?P<m>[\w]+)+&#160;(?P<d>\d{2})&#160;(?P<y>\d{4}),&#160;(?P<t>\d{2}:\d{2}:\d{2})&#160;CET(.*?)at Level\s(?P<level>[\d]+)'


def char_url(char_name):
    char_name = '+'.join(char_name.split())
    return f'https://www.tibia.com/community/?subtopic=characters&name={char_name}'


def guild_url(guild_name):
    guild_name = '+'.join(guild_name.split())
    return f'https://www.tibia.com/community/?subtopic=guilds&page=view&GuildName={guild_name}'


def parse_date(death_match):
    month, day, year, time = (death_match.group('m'),
                              death_match.group('d'),
                              death_match.group('y'),
                              death_match.group('t'))
    date_str =f'{month} {day} {year}, {time}'
    return datetime.datetime.strptime(date_str, '%b %d %Y, %H:%M:%S')


def fetch(url):
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
        yield (' '.join(name for name in member.group('char_name').split('+')),
               member.group('vocation'),
               int(member.group('level')))


def char_deaths(html):
    for death in find_deaths(html):
        yield parse_date(death), death.group('level')


def fetch_all(guilds, min_level):
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
