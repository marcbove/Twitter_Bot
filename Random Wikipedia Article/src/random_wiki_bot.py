import tweepy
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time
import yaml

MAX_CHAR = 240

with open(r'../../util/keys.yaml') as f:
    try:
        keys = yaml.safe_load(f)
    except yaml.YAMLError as err:
        print(err)
    else:
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_secret = keys['access_secret']


def extract_text():
    regex = re.compile('\[.]')
    txt = ''

    with urlopen('https://en.wikipedia.org/wiki/The_Son_of_the_Red_Corsair_(1943_film)') as response:
    # with urlopen('https://en.wikipedia.org/wiki/Special:Random') as response:
        url = response.geturl()
        soup = BeautifulSoup(response, 'html.parser')

    for p in soup.find_all('p'):
        txt += p.getText()

    txt = re.sub(regex, '', txt)

    return txt, url


def compose_tweet(s, u):
    proto_tweet = twt = ''
    u = '.\n' + u

    for i in range(len(s)):
        proto_tweet += s[i]
        if len(proto_tweet + u) < MAX_CHAR:
            twt = proto_tweet
        else:
            return twt + u


if __name__ == '__main__':
    sentences = ['']
    web = ''

    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_secret)
    # api = tweepy.API(auth)

    while True:
        text = ''
        while len(text) <= MAX_CHAR:
            text, web = extract_text()

        sentences = [x for x in map(str.strip, text.split('.')) if x]
        tweet = compose_tweet(sentences, web)

        print(tweet)
        time.sleep(60)
        # api.update_status(tweet)
