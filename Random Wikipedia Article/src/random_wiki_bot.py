import re
import tweepy
import yaml
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Constants
MAX_CHAR = 240
MIN_SENTENCES = 140

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
        link = response.geturl()[8:]
        soup = BeautifulSoup(response, 'html.parser')

    for p in soup.find_all('p'):
        txt += p.getText()

    txt = re.sub(regex, '', txt)
    txt = re.sub(' +', ' ', txt)
    txt = [x for x in map(str.strip, txt.split('. ')) if x]

    return txt, link


def compose_tweet(s):
    proto_tweet = twt = ''

    for i in range(len(s)):
        proto_tweet += s[i] + '. '
        if len(proto_tweet) < MAX_CHAR:
            twt = proto_tweet
        else:
            return twt, i


def not_interesting(sentence_array):
    return (sentence_array == '') or \
           (sum([len(x) for x in sentence_array]) < MAX_CHAR) or \
           (len(sentence_array[0]) > MAX_CHAR) or \
           (len(sentence_array) < MIN_SENTENCES)


if __name__ == '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    url = ''
    sentences = ['']

    while True:
        while not_interesting(sentences):
            sentences, url = extract_text()

        tweet, num_sentences = compose_tweet(sentences)

        if num_sentences > 0:
            try:
                status = api.update_status(status=tweet)
                api.update_status(status=url, in_reply_to_status_id=status.id)
            except tweepy.error.TweepError:
                print('DUPLICATED TWEET')
            print(tweet)
            time.sleep(14400)
