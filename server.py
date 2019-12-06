#!/usr/bin/python3

import os
import re
import urllib.request
import random

from flask import Flask, render_template
import feedparser


RSS_feeds = ['https://9gag-rss.com/api/rss/get?code=9GAGAwesome&format=2']

root_dir = os.getcwd()
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

cache = {}
patterns = [r'"https://[^\"]*?\.jpg"', r'"https://[^\"]*?\.mp4"', r'"https://[^\"]*?\.webm"',
            r'"http://[^\"]*?\.jpg"', r'"http://[^\"]*?\.mp4"', r'"http://[^\"]*?\.webm"']
cnt = 0


@app.route('/')
def index():
    global cnt
    
    feed = feedparser.parse(RSS_feeds[0])
    for item in feed['entries']:
        mch = []
        for pat in patterns:
            mch += re.findall(pat, item['summary'])
        for content in mch:
            # naive method: only randomly cache 10% contents
            # in reality, we may need to cache contents viewed most by users
            rnd = random.uniform(0, 1)
            if rnd < 0.9:
                continue
            
            url = content[1:-1]     # strip quotes
            print("URL to cache:", url)
            if url in cache:        # already cached
                item['summary'] = item['summary'].replace(url, "file://{}/{}".format(root_dir, cache[url]))
                print("Cache hit:", cache[url])
            else:
                try:
                    file_name = 'cache/' + str(cnt) + (url[-5:] if url[-1] == 'm' else url[-4:])
                    urllib.request.urlretrieve(url, file_name)
                    cnt += 1
                    cache[url] = file_name
                    print("Save cache to %s" % cache[url])
                    item['summary'] = item['summary'].replace(url, "file://{}/{}".format(root_dir, cache[url]))
                except Exception as e:
                    print(e)
                    pass

            print("Updated item summary:", item["summary"])
    
    return render_template('index.html', articles=feed['entries'])


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """
        print("running on %s:%d" % (host, port))
        app.run(host=host, port=port, debug=debug, threaded=threaded)

    run()
