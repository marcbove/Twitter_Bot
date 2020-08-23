import tweepy
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time
import yaml

# Constants
MAX_CHAR = 240
MIN_SENTENCES = 50

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
    regex = re.compile('\(.+?\)|\[.+?\]')
    txt = ''

    with urlopen('https://en.wikipedia.org/wiki/Special:Random') as response:
        url = response.geturl()[8:]
        soup = BeautifulSoup(response, 'html.parser')

    for p in soup.find_all('p'):
        txt += p.getText()

    txt = re.sub(regex, '', txt)
    txt = re.sub(' +', ' ', txt)
    txt = [x for x in map(str.strip, txt.split('. ')) if x]

    return txt, url


def compose_tweet(s, u):
    proto_tweet = twt = ''
    u = '\n' + u
    loops = 0

    for i in range(len(s)):
        proto_tweet += s[i] + '. '
        if len(proto_tweet + u) < MAX_CHAR:
            twt = proto_tweet
            loops += 1
        else:
            return twt + u, loops


def not_interesting(sentence_array):
    return (sentence_array == '') or \
           (sum([len(x) for x in sentence_array]) < MAX_CHAR) or \
           (len(sentence_array[0]) > MAX_CHAR) or \
           (len(sentence_array) < MIN_SENTENCES)


if __name__ == '__main__':

    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_secret)
    # api = tweepy.API(auth)
    asd = 0
    while asd < 15:
        asd += 1
        web = ''
        sentences = ['']

        while not_interesting(sentences):
            sentences, web = extract_text()

        tweet, err = compose_tweet(sentences, web)

        if err > 0:
            time.sleep(10)
            print(tweet)
            # api.update_status(tweet)
