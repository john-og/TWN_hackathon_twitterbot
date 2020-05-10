import tweepy
import json
import datetime
import nltk
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer

NUM_OF_IMAGES = 20

sia = SentimentIntensityAnalyzer()

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
user = api.get_user('twitter')

def getReplyScore(tweet):
    replies = tweepy.Cursor(api.search, q='to:{}'.format('@' + tweet.user.name), since_id=tweet._json['id_str'], tweet_mode='extended').items()
    score = tweet.favorite_count + tweet.retweet_count
    adjustment_score = 0

    while True:
        try:
            reply = replies.next()
            match = re.match(r'@.+ ', reply.full_text)
            if match is not None:
                polarity_info = sia.polarity_scores(reply.full_text[match.end():])
                adjustment_score += polarity_info['pos'] - polarity_info['neg'] + polarity_info['neu']
                print(polarity_info)
        except StopIteration:
            break

    score = score * (1.0 + adjustment_score / 10)
    print(score)
    return score

def getReplies(tweet):
    replies = tweepy.Cursor(api.search, q='to:{}'.format('@' + api.me().screen_name), since_id=tweet._json['id_str'], tweet_mode='extended').items()
    replies_arr = []

    while True:
        try:
            r = replies.next()

            try: 
                mediaExists = r.entities["media"]
            except:
                continue

            if not hasattr(r, 'in_reply_to_status_id_str'):
                continue
            if r.in_reply_to_status_id_str == tweet.id_str:
                score = getReplyScore(r)
                replies_arr.append({'reply': r, 'score': score})
                
        except tweepy.RateLimitError as e:
            logging.error('Twitter api rate limit reached'.format(e))
            time.sleep(60)
            continue

        except tweepy.TweepError as e:
            logging.error('Tweepy error occured:{}'.format(e))
            break

        except StopIteration:   
            break

        except Exception as e:
            logger.error('Failed while fetching replies {}'.format(e))
            break
        
    replies_arr = sorted(replies_arr, key=lambda i: i['score'], reverse=True)
    replies_arr = replies_arr[:NUM_OF_IMAGES]
    return replies_arr
        

while True:
    tweet_time = datetime.datetime.now()
    new_tweet = api.update_status(f'{tweet_time}\nReveal the remarkable in your day! Reply with pictures and videos of the weather around you for a chance to win a shoutout and other prizes. Previous winners can be found on our instagram @weathernetwork and on our app.')
    while True:
        delta = datetime.datetime.now() - tweet_time
        if (delta.seconds > 60):
            index = int(input("Choose an image (0-19): "))
            replies_arr = getReplies(new_tweet)
            try:
                api.update_status(f"The shot of the week is {replies_arr[index]['reply'].entities['media'][0]['media_url']} from @{replies_arr[index]['reply'].user.screen_name}. Congratulations! Check out our other winners on our instagram @weathernetwork and on our app.")
                break
            except IndexError:
                print('Out of range, please try again.')
