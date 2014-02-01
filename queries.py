import sqlite3
import argparse 
import pprint

DATABASE = "tweets.db"

def handle_command_line():
    parser = argparse.ArgumentParser(description="Gallup bot summaries")
    parser.add_argument("-c", "--create", help="create tables question and votes", action="store_true")
    parser.add_argument("-q", "--question", help="Current question", action='store_true')
    parser.add_argument("-s", "--summary", help="Get stats for the last tweeted question", action='store_true')
    parser.add_argument("-v", "--version", help="Get version information about the system", action="store_true")
    parser.add_argument("-a", "--answer", help="Add EMT answer to latest question", action="store_true")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	args = handle_command_line()
	c = get_cursor()
	pp = pprint.PrettyPrinter(indent=4)
	if args.summary:
		pass
	elif args.question:
		c.execute("select * from questions")
		pp.pprint(c.fetchall())
	elif args.create:
		create_table(c)
	elif args.version:
		print "Module version %s, Sqlite version %s" % (sqlite3.version, sqlite3.sqlite_version)
	elif args.answer:
		add_answer(c)
	c.close()
