import praw
import config
import time
import os
import unicodedata

keyword = 'respect'
subreddit_list = ['whowouldwin', 'respectthreads', 'characterrant', 'test']

posts_list = []

def bot_login():
	print('Logging in...')
	r = praw.Reddit(username = config.username,
				password = config.password,
				client_id = config.client_id,
				client_secret = config.client_secret,
				user_agent = 'respectthread responder v0.1')
	print('Logged in')
	with open("saved_posts.txt", "a") as f:
		f.write('\n')
	return r

class LineResults:
	def __init__(self, linelist, searchResults):
		self.linelist = linelist
		self.searchResults = searchResults

def run_bot(r):
	for sub in subreddit_list:
		# loop through every comment on a certain subreddit. Limits to 30 comments.
		quantity = 20
		print('Obtaining ' + str(quantity) + ' comments from r/' + sub + '...')
		for comment in r.subreddit(sub).comments(limit=quantity):
			resultList = []
			replyTo = False

			if comment.author != r.user.me() and comment not in posts_list and keyword in comment.body.lower():
				bodylist = comment.body.split('\n')
				for line in bodylist:
					linelist = line.split()
					if len(linelist) >= 2:
						if linelist[0].lower() == keyword or (linelist[1].lower() == keyword and (linelist[0] == '-' or linelist[0] == '*' or linelist[0] == '+')):
							searchResults = generate_search_results(linelist)
							resultList.append(LineResults(linelist, searchResults))
							replyTo = True

				if replyTo:
					generate_reply(comment, resultList)

	sleep_time = 20
	print('Sleeping for ' + str(sleep_time) + ' seconds...')
	time.sleep(sleep_time)

def generate_search_results(linelist):
	if linelist[0].lower() == keyword:
		linelist.pop(0)
	elif linelist[1].lower() == keyword and (linelist[0] == '-' or linelist[0] == '*' or linelist[0] == '+'):
		linelist.pop(0)
		linelist.pop(0)

	query = ''
	for string in linelist:
		query += string + ' '

    # Remove extra space at end of string
	query = query[:-1]

	searchResults = r.subreddit('respectthreads').search(query, sort='relevance', syntax='lucene', time_filter='all')
	filteredResults = []

	# Separate between bracketed and unbracketed user text, and remove accents.
	bracketedQuery = strip_accents(substring_in_brackets(query))
	unbracketedQuery = strip_accents(substring_out_brackets(query))

    # If the user specified the version or verse in brackets
	if len(bracketedQuery) > 0:
		for post in searchResults:
			# Separate between bracketed and unbracketed title text, and remove accents.
			unbracketedTitle = strip_accents(substring_out_brackets(post.title))
			bracketedTitle = strip_accents(substring_in_brackets(post.title))

			# Check for matches between user text and post title.
			if unbracketedQuery in unbracketedTitle and bracketedQuery in bracketedTitle:
				filteredResults.append(post)
	# Else if the user only specified the name
	else:
		for post in searchResults:
			unbracketedTitle = strip_accents(substring_out_brackets(post.title))
			if unbracketedQuery in unbracketedTitle:
				filteredResults.append(post)

	return filteredResults

def substring_in_brackets(query):
	A = list(query)
	inBrackets = False
	c = 0
	while c < len(A):
		if not inBrackets:
			if A[c] == '(' or A[c] == '[':
				inBrackets = True
			del A[c]
		else:
			if A[c] == ')' or A[c] == ']':
				inBrackets = False
				del A[c]
			else:
				c += 1

	return ''.join(A).lower().strip()

def substring_out_brackets(query):
	A = list(query)
	inBrackets = False

	c = 0
	while c < len(A):
		if not inBrackets:
			if A[c] == '(' or A[c] == '[':
				inBrackets = True
			else:
				c += 1
		else:
			if A[c] == ')' or A[c] == ']':
				inBrackets = False
			del A[c]
			
	return ''.join(A).lower().strip()

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        #print("NameError")
        pass

    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return str(text).replace("-", " ") # Remove dashes

def generate_reply(comment, resultList):
	replyText = ''
	for result in resultList:
		query = ' '.join(result.linelist)
		if result.searchResults:
			replyText += 'Here\'s what I found on r/respectthreads for *' + query + '*:\n\n'
			for searchResult in result.searchResults:
				replyText += '- [' + searchResult.title + '](' + searchResult.shortlink + ')' + '\n\n'
		else:
			replyText += 'Sorry, I couldn\'t find anything on r/respectthreads for *' + query + '*\n\n'

		replyText += '***\n\n'

	replyText += '^(I am a bot) ^| '
	replyText += '[^(About)](https://redd.it/bd2mld) ^| '
	replyText += '[^(How to use)](https://redd.it/bd2iv9) ^| '
	replyText += '[^(Code)](https://pastebin.com/gaU5qTmD) ^| '

	comment.reply(replyText)
	print(replyText)
	with open("saved_posts.txt", "a") as f:
		f.write(comment.id + '\n')
	posts_list.append(comment.id)
	resultList = []

def get_saved_posts():
	# Make sure the file exists.
	if not os.path.isfile("saved_posts.txt"):
		posts_list = []
	else:
		# "r" is to read from saved_posts.txt as the variable f
		with open("saved_posts.txt", "r") as f:
			posts_list = f.read()
			posts_list = posts_list.split("\n")
	return posts_list

posts_list = get_saved_posts()
r = bot_login()
while True:
	run_bot(r)
