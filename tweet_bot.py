import json
import codecs
import oauth2 as oauth
import datetime
import time as t
from credentials import *

TWEET_URL = "https://api.twitter.com/1.1/statuses/update.json"

def initialize_client(consumer_key, consumer_secret, access_key, access_secret):
    global client
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=access_key, secret=access_secret)
    client = oauth.Client(consumer, token)

class Bot:
    def __init__(self, tweets=[], counter=0, filename=None, interval=10):
        # If tweets list wasn't passed, open file and read everything but the first line
        # first line contains the counter
        if not tweets:
            try:
                with codecs.open(filename, 'r', 'utf-8') as f:
                    lines = f.readlines()
                    # For some reason a \ufeff sometimes appears in front of the number
                    lines[0] = lines[0].replace('\ufeff', '') # get rid of it
                    self.counter = int(lines[0])
                    self.tweets = lines[1:]
                    self.filename = filename
            except:
                print("Error opening the file")
                quit()
        else:
            self.tweets = tweets
            self.counter = counter
        self.interval = interval

    # may come in useful in later programs, hence static
    @staticmethod
    def oauth_req(client, url, post_body="", http_method="POST"):
    	response, data = client.request(url, method=http_method, body=post_body)
    	return response, data

    @staticmethod
    def tweet(client, msg):
        # encode message into URL format
        tweet_msg = oauth.urlencode({'status': msg})
        response, data = Bot.oauth_req(client, TWEET_URL, tweet_msg)
        print("Tweeting \"{}\", HTTP: {}".format(msg.strip(), response.status))


    def run(self):
        while True:
            time = datetime.datetime.now().time()
            minute = time.minute
            second = time.second

            # if the minute is a multiple of the interval and second == 0, send a tweet and increment the counter
            if not minute % self.interval and not second:
                # when the counter gets to the end, wrap around to the start using modulus
                __class__.tweet(client, self.tweets[self.counter % len(self.tweets)])
                self.counter += 1
                with codecs.open(self.filename, "w", "utf-8") as f:
                    tweets = "".join(self.tweets)
                    f.write(str(self.counter) + "\r\n" + tweets)

            t.sleep(1) # Sleep for a second to avoid posting multiple tweets



def main():
    initialize_client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    bot = Bot(filename="transcript.txt")
    bot.run()

if __name__ == '__main__':
    main()
