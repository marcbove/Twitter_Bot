# libraries
import collections

import tweepy
import yaml
import time
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from selenium import webdriver


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


def population_growth():
    driver = webdriver.Chrome(r'..\drv\chromedriver.exe')
    driver.get('https://www.worldometers.info/')

    bs = BeautifulSoup(driver.page_source, features='html.parser')

    births = bs.find('div', attrs={'data-target': '#births_this_year'}).text
    births_value = int(births.replace(',', '')[:-16])

    deaths = bs.find('span', attrs={'rel': 'dth1s_this_year'}).text
    deaths_value = int(deaths.replace(',', '')[1:])

    return births_value, deaths_value


def create_tweet(bths, dths):
    net_growth = bths - dths
    if bths > 0:
        bths = '+' + str(bths)
    if dths > 0:
        dths = '+' + str(dths)
    if net_growth > 0:
        net_growth = '+' + str(net_growth)
    return 'Since last hour:\n     Births: {}\n     Deaths: {}\n     World population: {}\n#World #Population #Growth #Bot'\
        .format(bths, dths, net_growth)


class CircularQueue:
    # Constructor
    def __init__(self, size):
        self.queue = collections.deque(maxlen=size)
        self.head = 0
        self.tail = 0
        self.maxSize = size

    # Adding elements to the queue
    def enqueue(self, data):
        if self.size() == self.maxSize-1:
            self.dequeue()
        self.queue.append(data)
        self.tail = (self.tail + 1) % self.maxSize
        return True

    # Removing elements from the queue
    def dequeue(self):
        if self.size() == 0:
            return "Queue Empty!"
        data = self.queue[self.head]
        self.head = (self.head + 1) % self.maxSize
        return data

    # Calculating the size of the queue
    def size(self):
        if self.tail >= self.head:
            return self.tail - self.head
        return self.maxSize - (self.head-self.tail)

    def get_queue(self):
        return self.queue


if __name__ == "__main__":
    #auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    #auth.set_access_token(access_token, access_secret)
    #api = tweepy.API(auth)
    births_last_hour = 0
    deaths_last_hour = 0
    MAX_SIZE = 8
    population = CircularQueue(MAX_SIZE)
    date = CircularQueue(MAX_SIZE)
    births = CircularQueue(MAX_SIZE)
    deaths = CircularQueue(MAX_SIZE)
    first_round = True
    plt.style.use('ggplot')

    while True:
        if first_round:
            with open('../data/population_data.yaml') as d:
                data = yaml.safe_load(d)

            for day in data.items():
                date.enqueue(day[0])
                population.enqueue(day[1]['net_lh'])
                births.enqueue(day[1]['births_lh'])
                deaths.enqueue(day[1]['deaths_lh'])

            births_last_hour = population.get_queue()[len(births.get_queue()) - 1]
            deaths_last_hour = population.get_queue()[len(deaths.get_queue()) - 1]
            first_round = False
            population.dequeue()
            date.dequeue()

        else:
            brths, deths = population_growth()
            net_births = brths - births_last_hour
            net_deaths = deths - deaths_last_hour
            births_last_hour = brths
            deaths_last_hour = deths
            tweet = create_tweet(net_births, net_deaths)

            net = net_births - net_deaths
            day = str(time.localtime(time.time())[3]) + ':' + \
                  str(time.localtime(time.time())[4]) + ':' + \
                  str(time.localtime(time.time())[5]) + '\n' + \
                  str(time.localtime(time.time())[2]) + '/' + \
                  str(time.localtime(time.time())[1])

            population.enqueue(net)
            date.enqueue(day)

            #plt.figure(figsize=(120, 80))
            plt.xlabel('Date')
            plt.ylabel('Population')
            plt.plot(date.get_queue(), population.get_queue(), 'g-o')
            plt.savefig('../img/plot.png')

            dictionary = {}
            for day in date.get_queue():
                for (b, d, g) in zip(births.get_queue(), deaths.get_queue(), population.get_queue()):
                    dictionary[day] = {'births_lh': b, 'deaths_lh': d, 'net_lh': g}

            with open('../data/population_data.yaml', 'w') as d:
                yaml.safe_dump(dictionary, d)

            #api.update_with_media('../img/plot.png', tweet)
            print(tweet + '\n')
            time.sleep(2)
