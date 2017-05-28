import json
import codecs
import oauth2 as oauth
import datetime
import time as t
from credentials import *

TWEET_URL = "https://api.twitter.com/1.1/statuses/update.json"

def initialize_client(consumer_key, consumer_secret, access_key, access_secret):
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=access_key, secret=access_secret)
    client = oauth.Client(consumer, token)
    return client

class Bot:
    def __init__(self, name="historyiguess", counter=0, filename=None, interval=10):
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                self.tweets = f.readlines()
                self.filename = filename
        except IOError:
            print("Error opening the file")
            quit()
        self.counter = counter
        self.interval = interval
        self.name = name


    @staticmethod
    def tweet(client, msg):
        # encode message into URL format
        tweet_msg = oauth.urlencode({'status': msg})
        # send HTTP request
        response, data = client.request(TWEET_URL, body=tweet_msg, method="POST")

        try: # Log the tweet to the console with the HTTP status
            print("Tweeting \"{}\", HTTP: {}".format(msg.encode("utf-8").strip(), response.status))
        except UnicodeEncodeError:
            print("Failed encoding tweet for debug print")

        return response, data


    def run(self):
        while True:
            time = datetime.datetime.now().time()
            minute = time.minute
            second = time.second

            # if the minute is a multiple of the interval and second == 0, send a tweet and increment the counter
            if not minute % self.interval and not second:
                for i in range(4): # Try to post 4 times in case an error occurs
                    client = initialize_client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
                    try:
                        # Get data containing number of tweets
                        response, data = client.request("https://api.twitter.com/1.1/users/show.json?screen_name=" + self.name, method="GET")
                        # Parse the data to set the counter
                        parse = json.loads(data.decode('latin1'))
                        self.counter = int(parse["statuses_count"])
                    except:
                        continue # Try again if parsing failed due to an error

                    # when the counter gets to the end, wrap around to the start using modulus
                    msg = self.tweets[self.counter % len(self.tweets)]
                    response, data = __class__.tweet(client, msg)

                    if response.status in [200, 403]: # If successfully sent, or duplicate tweet
                        break # No need to try post again, break out of the loop
                    else:
                        print(data)
            t.sleep(1) # Sleep for a second to avoid posting multiple tweets



def main():
    bot = Bot(filename="transcript.txt")
    bot.run()

if __name__ == '__main__':
    main()
