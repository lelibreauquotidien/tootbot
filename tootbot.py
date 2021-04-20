import os.path
import sys
import re
import sqlite3
import configparser

from datetime import datetime, timedelta
import feedparser
from mastodon import Mastodon
import requests
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--configuration', help='Configuration file emplacement', required=True)
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.configuration)

mstdn = config["MASTODON"]
nitter = config["NITTER"]
source = config["SOURCE"]
print("TOOTBOT, official git forge: https://github.com/lelibreauquotidien/tootbot")

# sqlite db to store processed tweets (and corresponding toots ids)
print("[INFO]: Connect sqlite3 database")
sql = sqlite3.connect('tootbot.db')
db = sql.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS tweets (tweet text, toot text,
           twitter text, mastodon text, instance text)''')

print("[INFO]: Pull ini configuration file")

instance = mstdn["instance"]
days = int(mstdn["days"])
tags = mstdn["tags"]
delay = int(mstdn["delay"])
source = source["twitter"]
login = mstdn["login"]
passwd = mstdn["passwd"]

mastodon_api = None


print("[INFO]: Parse rss...")

url = nitter["instance"]+source+'/rss'
print(url)
rss_feed = feedparser.parse(url)
twitter = source
print('for')
for tweet in reversed(rss_feed.entries):
    # check if this tweet has been processed
    db.execute('SELECT * FROM tweets WHERE tweet = ? AND twitter = ?  and mastodon = ? and instance = ?', (tweet.id, source, login, instance))  # noqa
    # Get last published tweet
    last = db.fetchone()
    date = tweet.published_parsed
    age = datetime.now()-datetime(date.tm_year, date.tm_mon, date.tm_mday, date.tm_hour, date.tm_min, date.tm_sec)
 # process only unprocessed tweets less than 1 day old, after delay
    if last is None and age < timedelta(days=days) and age > timedelta(days=delay):
        if mastodon_api is None:
            # Create application if it does not exist
            print("[INFO]: Create mastodon application..")
            if not os.path.isfile(instance+'.secret'):
                if Mastodon.create_app(
                    'tootbot',
                    api_base_url='https://'+instance,
                    to_file=instance+'.secret'
                ):
                    print('[INFO]: tootbot app created on instance '+instance)
                else:
                    print('[ERROR]: Failed to create app on instance '+instance)
                    sys.exit(1)

            try:
                mastodon_api = Mastodon(
                    client_id=instance+'.secret',
                    api_base_url='https://'+instance
                )
                mastodon_api.log_in(
                    username=login,
                    password=passwd,
                    scopes=['read', 'write'],
                    to_file=login+".secret"
                )
            except:
                print("[ERROR]: Login Failed!")
                sys.exit(1)

        toot = tweet.title

        toot_media = []
        # get the pictures...
        for match in re.finditer("https://nitter.tedomum.net/pic/media(.*).jpg", tweet.summary):
            media = requests.get(match.group(0))
            media_posted = mastodon_api.media_post(media.content, mime_type=media.headers.get('content-type'))
            toot_media.append(media_posted['id'])


        if tags:
            toot = toot + '\n' + tags

        if toot_media is not None:
            print("[INFO]: Toot Posted: ", toot)
            toot = mastodon_api.status_post(toot, in_reply_to_id=None,
                                            media_ids=toot_media,
                                            sensitive=False,
                                            visibility='public',
                                            spoiler_text=None)
        if "id" in toot: 
            db.execute("INSERT INTO tweets VALUES ( ? , ? , ? , ? , ? )",
                        (tweet.id, toot["id"], source, login, instance))
            sql.commit()
