# TootBot

A small python 3.x script to replicate tweets on a mastodon account.

This repo is a fork of https://github.com/cquest/tootbot with a lot of changes :
* Use nitter
* More configuration possibilities
* .ini configuration file

The script only need mastodon login/pass to post toots.

A sqlite database is used to keep track of tweets than have been tooted.

The script is simply called by a cron job and can run on any server (does not have to be on the mastodon instance server).

## Setup

```
# clone this repo
git clone https://github.com/lelibreauquotidien/tootbot.git
cd tootbot

# install required python modules
pip3 install -r requirements.txt
```

## Usage
Create configuration file with the model (tootbot.ini.example)

Run :

`python3 tootbot.py -c your-tootbot-conf.ini`


It's up to you to add this in your crontab :)
