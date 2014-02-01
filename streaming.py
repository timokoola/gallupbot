import tweepy, sys, os
import argparse # requires 2.7
import random, re, daemon, lockfile, datetime
import json
import sqlite3

answerre = re.compile('([a-cA-C]+)')
useraccount = "@timotestikoola"

def handle_command_line():
    parser = argparse.ArgumentParser(description="Run streaming twitter bot")
    parser.add_argument("-t", "--test", help="Get a test response")
    parser.add_argument("-k", "--keyfile", help="Twitter account consumer and accesstokens")
    parser.add_argument("-u", "--username", help="Username to follow", default=useraccount)
    parser.add_argument("-q", "--question", help="Question to tweet")
    parser.add_argument("-s", "--summary", help="Get stats for the last tweeted question", action='store_true')
    args = parser.parse_args()
    return args


class AnswerParser:
    def __init__(self,description, prev):
        mth = answerre.match(description)
        if not mth:
             mth = answerre.match(prev)
        if mth:
            self.answer = mth.groups()[0]
        else:
            self.answer = "EMT"

def store_answer(answer, status, name):
    pass

class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        try:
            name = status.author.screen_name

            ap = AnswerParser(status.text, "EMT")
            store_answer(ap.answer, status, name)

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
    item = tweet.text.split("\n")
    storable_item = (item[0], item[1], item[2], item[3], datetime.datetime.now().isoformat(), tweet.id)
    c.execute('''INSERT INTO questions VALUES (NULL, ?, ?, ?, ?, ?, ?) ''', storable_item)
    conn.commit()
   


def question_from_file(f):
    fr = open(f)
    text = fr.read()
    fr.close
    return text
    

if __name__ == "__main__":
    args = handle_command_line()
    useraccount = args.username
    api = (TweepyHelper(args.keyfile)).api
    if args.question:
        twapi = (NormalTweepyHelper(args.keyfile)).api
        tweet = twapi.update_status(question_from_file(args.question))
        store_question(tweet)
        sys.exit(0)
    if args.summary:
        ltq = latest_question()
        print ltq, ltq[-1]
        sys.exit(0)

    ferr = open("runningstreamingerrs.txt", "w+")
    fout = open("runningstreamingout.txt", "w+")
    if not args.test:
        with daemon.DaemonContext(pidfile=lockfile.FileLock("streamingDaemon"), files_preserve=[ferr, fout], stderr=ferr, stdout=fout):
            run(api)
    else:
       run(api)
    conn.close()

