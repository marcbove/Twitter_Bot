import tweepy
import re
import yaml
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

with open(r'../util/keys.yaml') as f:
    try:
        keys = yaml.safe_load(f)
    except yaml.YAMLError as err:
        print(err)
    else:
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_secret = keys['access_secret']


def tweet_word():
    request = Request("https://www.merriam-webster.com/word-of-the-day")
    response = urlopen(request)
    url = response.geturl()

    bs = BeautifulSoup(response, 'html.parser')
    word = bs.h1.string
    mssg = r"Today's word: {}".format(word)

    definition_found = False
    for line in bs.get_text().split('\n'):
        if definition_found:
            if re.match("([0-9]|:).*", line):
                if re.match(":.*", line):
                    line = '1' + line
                mssg += '\n' + line
            else:
                return mssg + '\n' + url
        if line.lower() == 'definition':
            definition_found = True


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    message = tweet_word()
    print(message)
    api.update_status(message)
