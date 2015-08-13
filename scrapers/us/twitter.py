from urlparse import parse_qs
from requests_oauthlib import OAuth1
import psycopg2
import requests
import urllib2
import lxml.html
import json
import sys

CONSUMER_KEY = 'uXfYNwc2jrCv5uY5Qxbz5sSrD'
CONSUMER_SECRET = 'JN6qvJzzSlngNSMR6LVhvG8jt0mhhPLZtsaXm73P3Lc2mfj80F'
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

OAUTH_TOKEN = "61342023-oV67IkrGYyAt2tluyvEpyhcGAaNXJWhO86jxc62eD"
OAUTH_TOKEN_SECRET = "bCHhAcaGKVTbYsdALMrUwedVmnvfXKV6oMe9AvRd1er20"


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=OAUTH_TOKEN,
                   resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

if __name__ == "__main__":
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret

    else:
        oauth = get_oauth()
        doc = lxml.html.fromstring(urllib2.urlopen("http://govsm.com/w/House").read())
        for twitter_links in doc.xpath("//a[contains(@href, 'twitter')]"):
            twitter_handle = twitter_links.attrib['href'][20:]
            r = requests.get(url="https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s" %
                             twitter_handle, auth=oauth)
            for tweets in r.json():
                print tweets['text']
            break
