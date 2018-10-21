# Reddit respectthreads bot

**Version 0.1**

This bot searches through new comments on a single subreddit, most likely r/whowouldwin. It looks for comments that contain the word (case-insensitive) "respect". If it finds one, it splits the body of the comment into lines. For each line, if one of those lines start with "respect" or "- respect", it searches r/respectthreads for submissions with a similar title to the rest of the line.

For example, if the line is "Respect Thor (Marvel)" the bot's search function returns:
- [Respect Jane Foster: Thor (Marvel 616)](https://redd.it/6lz5ho)
- [Respect Odin-Force Thor (Marvel, 616)](https://redd.it/6w805j)
- [Respect Rune King Thor (Marvel 616)](https://redd.it/3lm2uh)
- [Respect Thor Odinson (Marvel Cinematic Universe)](https://redd.it/7udbao)
- [Respect: Thor Odinson (Marvel, 616)](https://redd.it/4vfjy5)

The bot then generates a reply using the search results, and the comments are given a list of links to the found respect threads.

## Prerequisites

Built With

* [PRAW](http://praw.readthedocs.io/en/latest/getting_started/installation.html) - The Python Reddit API Wrapper
* [Python 3.6.5](https://www.python.org/downloads/) - The programming language used by PRAW

## Authors

* **Luke Tran** - [Luke-Tran](https://github.com/Luke-Tran)