import sys
import os
import requests
import json
from bs4 import BeautifulSoup
import caching

URL_FORMAT = "https://emojipedia.org/search/?q={q}"


class Emoji:
    def __init__(self, slug, emoji, name):
        self.slug = slug
        self.emoji = emoji
        self.name = name

    def __str__(self):
        return "{emoji} {name} ({slug})".format(emoji=self.emoji, name=self.name, slug=self.slug)

    def __repr__(self):
        return str(self)


def getSearchString():
    if len(sys.argv) < 2:
        print("need a keyword to query")
        os._exit(1)

    q = sys.argv[1]
    return q


def composeURL(q):
    q = q.replace(' ', '+')
    return URL_FORMAT.format(q=q)


def extractEmoji(title):
    a = title.find("a")
    slug = a['href'][1:-1]
    results = [text for text in a.stripped_strings]
    return Emoji(slug, results[0], results[1])


def lookup(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    titles = soup.find("ol", "search-results").find_all("h2")
    emojis = []
    for title in titles:
        emojis.append(extractEmoji(title))
    return emojis


def output(emojis):
    data = {'items': []}
    for emoji in emojis:
        data['items'].append({
            'uid': emoji.slug,
            'title': emoji.emoji,
            'subtitle': emoji.name,
            'autocomplete': emoji.name,
            'text': {
                'copy': emoji.emoji,
                'largetype': emoji.emoji,
            }
        })
    return json.dumps(data, indent=2)


if __name__ == '__main__':
    caching.init()
    q = getSearchString()
    url = composeURL(q)
    emojis = lookup(url)
    caching.cacheEmojis(q, emojis)
    print(output(emojis))
