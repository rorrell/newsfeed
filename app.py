import time
from flask import Flask, render_template, request
import feedparser
import constants
from cachetools import cached, TTLCache

app = Flask(__name__)
cache = TTLCache(maxsize=100, ttl=3600)

def get_entries(name, url, news):
    entries = feedparser.parse(url).entries
    for entry in entries:
        entry['source'] = name
        if 'published_parsed' in entry:  # because not all entries have a date
            entry['date'] = entry['published_parsed']
        else:
            entry['date'] = time.localtime(time.time())
        news.append(entry)

@cached(cache)
def get_news(source=''):
    news = []

    if source == '':
        for name, url in constants.rss.items():
            get_entries(name, url, news)
    else:
        get_entries(source, constants.rss[source], news)

    news.sort(key=lambda x: x['date'], reverse=True)
    return news


@app.route('/')
def home():
    args = request.args

    source = args.get('source')
    if source is None:
        source = ''
    news = get_news(source)

    page = args.get('page')
    tmp = [news[i:i+25] for i in range(0, len(news), 25)]
    nxt = -1
    prev = -1
    if page is not None and int(page) > 1:
        news = tmp[int(page)-1]
        prev = int(page) - 1
        if len(tmp) > int(page):
            nxt = int(page) + 1
    else:
        news = tmp[0]
        if len(tmp) > 1:
            nxt = 2

    return render_template('index.html', data=news, len=len(news), next=nxt,
                           prev=prev, select=constants.rss.keys(),
                           selected=source)


if __name__ == '__main__':
    app.run()
