import asyncio
import re
import datetime
import aiohttp

TIBIA_COMMUNITY_URL = 'https://www.tibia.com/community/'

"""
Guild member pattern. Finds members in guild page html. Ex:

&name=Alice+Spectre">Alice&#160;Spectre</A></TD>
<TD>Master Sorcerer</TD>
<TD>288</TD>

Please use https://regex101.com/ to test.
"""
guild_member = (r'&name=(?P<char_name>[\w\+%\d-]+)(.)+\s?'
                r'<TD>(?P<vocation>[\w\s]+)</TD>\s?'
                r'<TD>(?P<level>[\d]+)</TD>')
guild_member_pattern = re.compile(guild_member)

"""
Death pattern. Finds death entries in character page html. Ex:

valign="top">Nov&#160;26&#160;2019,&#160;21:36:23&#160;CET</td>
<td>Died at Level 1099 by an energetic book.<br />

Please use https://regex101.com/ to test.
"""
death = (r'top">(?P<m>[\w]+)+&#160;(?P<d>\d{2})&#160;(?P<y>\d{4}),&#160;(?P<t>\d{2}:\d{2}:\d{2})&#160;CET(.*?)'
         r'at Level\s(?P<level>[\d]+)')
death_pattern = re.compile(death)


def char_url(char_name):
    """Returns an url to the character's profile on tibia community."""
    char_name = '+'.join(char_name.split())
    return f'{TIBIA_COMMUNITY_URL}?subtopic=characters&name={char_name}'


def guild_url(guild_name):
    """Returns an url to the guild page on tibia community."""
    guild_name = '+'.join(guild_name.split())
    return f'{TIBIA_COMMUNITY_URL}?subtopic=guilds&page=view&GuildName={guild_name}'


def _parse_date(death_match):
    month, day, year, time = (death_match.group('m'),
                              death_match.group('d'),
                              death_match.group('y'),
                              death_match.group('t'))
    date_str = f'{month} {day} {year}, {time}'
    return datetime.datetime.strptime(date_str, '%b %d %Y, %H:%M:%S')


def _find_guild_members(html):
    for member in guild_member_pattern.finditer(html):
        yield member


def _find_deaths(html):
    for death in death_pattern.finditer(html):
        yield death


def guild_members(html):
    """Parses and yields guild members (char name, vocation, level) in
    the guild page."""
    for member in _find_guild_members(html):
        # transforms First+Last in First Last
        char_name = ' '.join(member.group('char_name').split('+'))
        yield (char_name.replace('%27', "'"),
               member.group('vocation'),
               int(member.group('level')))


def char_deaths(html):
    """Parses and yields death entries in the character's page."""
    for death in _find_deaths(html):
        yield _parse_date(death), int(death.group('level'))


async def fetch(session, url):
    async with session.get(url) as response:
        assert 200 == response.status, response.status
        return await response.text()


async def _fetch_all(guilds, min_level, timeout=1200, limit=10):
    conn = aiohttp.TCPConnector(limit_per_host=limit)
    _timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(connector=conn, timeout=_timeout) as session:

        guild_urls = [guild_url(guild) for guild in guilds]
        guild_pages = await asyncio.gather(
            *(fetch(session, url) for url in guild_urls)
        )

        # go through guild pages -> character pages
        # and store all deaths in a list
        deaths = []
        for guild_name, guild_page in zip(guilds, guild_pages):
            # select characters level greater than minimun level filter
            chars = []
            for char_name, voc, level in guild_members(guild_page):
                if level >= min_level:
                    chars.append((char_name, voc, level))

            # fetch the characters pages
            char_pages = await asyncio.gather(
                *(fetch(session, char_url(char[0])) for char in chars)
            )

            # parse death entries in character page
            for char, char_page in zip(chars, char_pages):
                for date, level in char_deaths(char_page):
                    deaths.append({
                        'char_name': char[0],
                        'level': level,
                        'vocation': char[1],
                        'datetime': date,
                        'guild': guild_name,
                    })
        return deaths


def fetch_all(guilds, min_level):
    return asyncio.run(_fetch_all(guilds, min_level))
