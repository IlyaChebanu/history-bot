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
    def __init__(self, tweets=[], counter=0, filename=None, interval=10):
        # If tweets list wasn't passed, open file and read everything but the first line
        # first line contains the counter
        if not tweets:
            try:
                with codecs.open(filename, 'r', 'utf-8') as f:
                    lines = f.readlines()
                    # For some reason a \ufeff sometimes appears in front of the number
                    lines[0] = lines[0].replace('\ufeff', '') # get rid of it
                    self.counter = int(lines[0]) # first line
                    self.tweets = lines[1:] # rest of file
                    self.filename = filename
            except ValueError:
                print("Failed to set the counter")
                quit()
            except IOError:
                print("Error opening the file")
                quit()
        else: # if a list of tweets was supplied
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
        # send HTTP request
        response, data = Bot.oauth_req(client, TWEET_URL, tweet_msg)

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
                    # when the counter gets to the end, wrap around to the start using modulus
                    msg = self.tweets[self.counter % len(self.tweets)]
                    response, data = __class__.tweet(client, msg)

                    if response.status in [200, 403]: # If successfully sent, or duplicate tweet
                        self.counter += 1

                        if self.filename: # If reading from a file, increment file's counter
                            with codecs.open(self.filename, "w", "utf-8") as f:
                                tweets = "".join(self.tweets)
                                f.write(str(self.counter) + "\r\n" + tweets)
                        break
                    else:
                        print(response.error)
            t.sleep(1) # Sleep for a second to avoid posting multiple tweets



def main():
    bot = Bot(filename="transcript.txt")
    bot.run()

if __name__ == '__main__':
    main()
