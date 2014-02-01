import sqlite3
import datetime

DATABASE = "tweets.db"
TWEETID_FIELD = -1


class Question(object):
    """represents the question"""
    def __init__(self, question, answer_a, answer_b, answer_c):
        self.question = question
        self.answer_a = answer_a
        self.answer_b = answer_b
        self.answer_c = answer_c

    @classmethod
    def create_from_file(cls, filename):
        """Create question from a file"""
        f = open(filename)
        lines = f.read().split("\n")
        f.close()
        return Question(lines[0],lines[1], lines[2], lines[3])

    def set_tweetid(self, tweetid):
        """Associate tweetid to the question"""
        self.tweetid = tweetid

    def __repr__(self):
        return "\n".join([self.question, self.answer_a, self.answer_b, self.answer_c])

class DbFacade(object):
    """Class that acts as a clue between the database 
    and the rest of the script"""
    def __init__(self, db=DATABASE):
        """Constructor that initializes the db connection"""
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def close(self):
        """Close the database connection"""
        self.connection.close()

    def create_tables(self):
        """Creates the tables in the local database"""
        self.cursor.execute("pragma foreign_keys=on;")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS questions (questionid INTEGER PRIMARY KEY, question TEXT, answer_a TEXT,answer_b TEXT, answer_c TEXT, timestamp text, tweetid TEXT) ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS answer (voteid INTEGER, vote TEXT, name TEXT, timestamp text, tweetid text, FOREIGN KEY(voteid) REFERENCES questions(questionid)) ''')

    def set_current_question(self,question):
        """Set current question to the database"""
        storable_item = (question.question, question.answer_a, question.answer_b, question.answer_c, datetime.datetime.now().isoformat(), tweet.id)
        self.cursor.execute('''INSERT INTO questions VALUES (NULL, ?, ?, ?, ?, ?, ?) ''', storable_item)
        self.conn.commit()

    def get_current_question(self):
        """Get the currently active question"""
        self.cursor.execute("select * from questions order by timestamp DESC limit 1")
        return self.cursor.fetchone()

    def add_answer(self, name, question, answer):
        """Creates answer in current question
        name is the username, question is the question being answered (original tweet), and answer"""
        current_id = self.get_current_question[TWEETID_FIELD]
        self.cursor.execute('REPLACE INTO answer (?)', (None, answer, name, datetime.datetime.now().isoformat(),question.selfid))
        self.connection.commit()

