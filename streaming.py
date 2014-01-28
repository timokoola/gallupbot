import tweepy, sys, os
import argparse # requires 2.7
import random, re, daemon, lockfile
from pymongo import MongoClient
import json

answerre = re.compile('([a-cA-C]+)')
useraccount = "@gallupbot"
db_collection = None

def handle_command_line():
    parser = argparse.ArgumentParser(description="Run streaming twitter bot")
    parser.add_argument("-t", "--test", help="Get a test response")
    parser.add_argument("-k", "--keyfile", help="Twitter account consumer and accesstokens")
    parser.add_argument("-u", "--username", help="Username to follow", default="@gallupbot")
    parser.add_argument("-q", "--question", help="Question to tweet")
    parser.add_argument("-s", "--summary", help="Get stats for the last tweeted question")
    args = parser.parse_args()
    return args


class AnswerParser:
    def __init__(self,description,prev):
        mth = answerre.match(description)
        if not mth:
             mth = answerre.match(prev)
        if mth:
            self.answer = mth.groups()[0]
        else:
            self.answer = "EMT"

class ReplyGenerator:
    def __init__(self,tweet):
        self.tweet = tweet
        dp = AnswerParser(tweet.split()[1],"EMT")
        self.answer = dp.answer

    def reply(self):
        reply = "%s" % (self.answer)
        return reply


class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        
        # We'll simply print some values in a tab-delimited format
        # suitable for capturing to a flat file but you could opt 
        # store them elsewhere, retweet select statuses, etc.



        try:
            print "%s\t%s\t%s\t%s" % (status.text, 
                                      status.author.screen_name, 
                                      status.created_at, 
                                      status.source,)
            #yeah, needs refactoring
            # first  find the latest status we have created
            #self.tweepyapi.
            latest_id = latest_question()["id"]
            name = status.author.screen_name

            prev_answer = db_collection.find({"type": "answer", "name": name})

            if prev_answer.count() > 0:
                s = prev_answer[0]
            else:
                s = {}
                s["text"] = status.text
                s["name"] = name
                s["timestamp"] = status.created_at
            ap = AnswerParser(status.text)
            s["answer"] = ap.answer
            db_collection.save(s)

        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e
            pass

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

class TweepyHelper:
    def __init__(self,keyfile):
        f = open(keyfile)
        lines = f.readlines()
        f.close()
        consumerkey = lines[0].split("#")[0]
        consumersecret = lines[1].split("#")[0]
        accesstoken = lines[2].split("#")[0]
        accesssec = lines[3].split("#")[0]

        auth = tweepy.OAuthHandler(consumerkey, consumersecret)
        auth.set_access_token(accesstoken, accesssec)
        listener = CustomStreamListener()
        listener.tweepyapi = tweepy.API(auth)
        self.tweepyapi = listener.tweepyapi
        self.api = tweepy.streaming.Stream(auth, listener, timeout=60)

class NormalTweepyHelper:
    def __init__(self,keyfile):
        f = open(keyfile)
        lines = f.readlines()
        f.close()
        consumerkey = lines[0].split("#")[0]
        consumersecret = lines[1].split("#")[0]
        accesstoken = lines[2].split("#")[0]
        accesssec = lines[3].split("#")[0]

        auth = tweepy.OAuthHandler(consumerkey, consumersecret)
        auth.set_access_token(accesstoken, accesssec)
        self.api = tweepy.API(auth)

def run(api):
    api.filter(track=[useraccount])

def store_question(tweet):
    qs = {}
    qs["tweetid"] = tweet.id
    qs["text"] = tweet.text
    qs["type"] = "question"
    qs["timestamp"] = tweet.created_at
    db_collection.insert(qs) 

def latest_question():
    return db_collection.find({"type":"question"}).sort("_id", -1).limit(1)[0]

def question_from_file(f):
    fr = open(f)
    text = fr.read()
    fr.close
    return text
    
def connect_to_db():
    global db_collection
    client = MongoClient()
    db = client.answerstream
    db_collection = db.answercollection


if __name__ == "__main__":
    args = handle_command_line()
    connect_to_db()
    useraccount = args.username
    api = (TweepyHelper(args.keyfile)).api
    if args.question:
        twapi = (NormalTweepyHelper(args.keyfile)).api
        tweet = twapi.update_status(question_from_file(args.question))
        store_question(tweet)
        sys.exit(0)
    if args.summary:
        print latest_question()
        sys.exit(0)

    ferr = open("runningstreamingerrs.txt", "w+")
    fout = open("runningstreamingout.txt", "w+")
    if not args.test:
        with daemon.DaemonContext(pidfile=lockfile.FileLock("streamingDaemon"), files_preserve=[ferr, fout], stderr=ferr, stdout=fout):
            run(api)
    else:
       run(api)

