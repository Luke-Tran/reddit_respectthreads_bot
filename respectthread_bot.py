import praw 
import config
import time
import os

keyword = 'respect'
sub = 'test'

posts_list = []	

def bot_login():
	print('Logging in...')
	r = praw.Reddit(username = config.username,
				password = config.password,
				client_id = config.client_id,
				client_secret = config.client_secret,
				user_agent = 'respectthread responder v0.1')
	print('Logged in')
	return r

class LineResults:
	def __init__(self, linelist, searchResults):
		self.linelist = linelist
		self.searchResults = searchResults

def run_bot(r):
	resultList = []

	# loop through every comment on a certain subreddit. Limits to 25 comments.
	print('Obtaining 25 comments...')
	for comment in r.subreddit(sub).comments(limit=25):
		replyTo = False
		body = comment.body.lower()

		if comment.author != r.user.me() and comment not in posts_list and keyword in body:
			bodylist = body.split('\n')
			for line in bodylist:
				linelist = line.split()
				if len(linelist) >= 2:
					# For now, it won't check numbered lists.
					if linelist[0] == keyword or (linelist[1] == keyword and (linelist[0] == '-' or linelist[0] == '*' or linelist[0] == '+')):
						searchResults = generate_search_results(linelist)		
						resultList.append(LineResults(linelist, searchResults))
						replyTo = True

			if replyTo:
				generate_reply(comment, resultList)
	
	print('Sleeping for 20 seconds...')
	time.sleep(20)
		
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

	comment.reply(replyText)
	print(replyText)
	with open("saved_posts.txt", "a") as f:
		f.write(comment.id + '\n')
	posts_list.append(comment.id)
		
def generate_search_results(linelist):
	if linelist[0] == keyword:
		linelist.pop(0)
	elif linelist[1] == keyword and (linelist[0] == '-' or linelist[0] == '*' or linelist[0] == '+'):
		linelist.pop(0)
		linelist.pop(0)

	query = ''
	for string in linelist:
		query += string + ' '

	query = query[:-1]
	
	searchResults = r.subreddit('respectthreads').search(query, sort='relevance', syntax='lucene', time_filter='all')
	filteredResults = []
	
	bracketedQuery = substring_in_brackets(query)
	unbracketedQuery = substring_out_brackets(query)
		
	if len(bracketedQuery) > 0:
		for post in searchResults:
			unbracketedTitle = substring_out_brackets(post.title)
			bracketedTitle = substring_in_brackets(post.title)
			if unbracketedQuery in unbracketedTitle and bracketedQuery in bracketedTitle:
				filteredResults.append(post)
	else:
		for post in searchResults:
			unbracketedTitle = substring_out_brackets(post.title)
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
	
	return ''.join(A).lower()

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
	return ''.join(A).lower()

def get_saved_posts():
	#Make sure the file exists.
	if not os.path.isfile("saved_posts.txt"):
		posts_list = []
	else:
		#"r" is to read from saved_posts.txt as the variable f
		with open("saved_posts.txt", "r") as f:
			posts_list = f.read()
			posts_list = posts_list.split("\n")
	return posts_list	
	
posts_list = get_saved_posts()
r = bot_login()
while True:
	run_bot(r)
