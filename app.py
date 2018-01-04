#!/usr/bin/env python3

import datetime
import requests
import os
import io
import pickle
import textwrap
import praw
from PIL import Image

image_ua = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'

font = Image.open('font.png')

bot = praw.Reddit('redditx')

sub = bot.subreddit('all')

blacklisted_objects = {'silver', 'gold', 'garlic'}

if not os.path.isdir('cache'):
	os.mkdir('cache')

cached_objects = set([i[:-4] for i in os.listdir('cache')])

gift_history = dict()

if os.path.isfile('history.dat'):
	with open('history.dat', 'rb') as f:
		gift_history = pickle.load(f)

def addandgethist(usr, what):
	
	usr = usr.fullname

	if usr not in gift_history:
		gift_history[usr] = dict()
	
	usr_hist = gift_history[usr]

	usr_hist[what] = 1 + usr_hist.get(what, 0)

	savehist()

	has = sorted(usr_hist.items(), key=lambda x: -x[1])

	has = ['{} {} time{}'.format(i[0].replace('_', ' '), i[1], '' if i[1] == 1 else 's') for i in has]

	if len(has) > 1:
		has[-2] = has[-2] + ' and ' + has[-1]
		has = has[:-1]
	
	has = ', '.join(has)

	return has

def savehist():
	with open('history.dat', 'wb') as f:
		pickle.dump(gift_history, f)

def drawchar(img, char, x, y):
	
	c = ord(char.upper()) - ord('A')

	if c not in range(26):
		return
	
	for i in range(32):
		if 0 <= i + x < img.width:
			for j in range(32):
				clr = font.getpixel((i + 32 * c,j))
				if clr[3] == 255:
					img.putpixel((i + x, j + y), clr)

def drawtext(img, what):
	
	x = img.width // 2 - 96
	y = img.height // 2 - 48

	for c in 'REDDIT':
		drawchar(img, c, x, y)
		x += 32
	
	x = img.width // 2 - 16 * len(what)
	y += 64

	for c in what:
		drawchar(img, c, x, y)
		x += 32

def handle(comment):
	
	body = comment.body

	what = ''
	for c in body[7:]:
		if c in 'qwertyuiopasdfghjklzxcvbnmMNBVCXZLKJHGFDSAPOIUYTREWQ_':
			what += c
		else:
			break

	what = what.lower().strip('_')

	if (not what) or what in blacklisted_objects:
		return

	rem = body[7 + len(what):].strip()

	who = None

	if rem.startswith('u/') or rem.startswith('/u/'):
		un = rem.split('u/', 1)[1]
		i = 0
		while i < len(un):
			if un[i] not in 'qwertyuiopasdfghjklzxcvbnmMNBVCXZLKJHGFDSAPOIUYTREWQ1234567890_-':
				break
			i += 1
		un = un[:i]
		who = bot.redditor(un)
	
	else:
		who = comment.parent().author

	if who.fullname == comment.author.fullname:
		return
	
	print('[{}] [Comment {}] User {} gave user {} a !reddit{}'.format(datetime.datetime.now().isoformat(), comment.fullname, comment.author.name, who.name, what))

	create_image(what)

	post = textwrap.dedent('''
		**[Here's your Reddit {nani}, {usr}!](http://interwebs.cf/reddit-x-bot/{what}.png)**

		/u/{usr} has received {hist}. (given by /u/{giver}) **[info](https://github.com/gemdude46/redditx)**
	''').format(what=what, nani=what.replace('_', ' ').capitalize(), usr=who.name, giver=comment.author.name, hist=addandgethist(who, what))

	print(post)

def create_image(what):
	if what not in cached_objects:

		nani = what.replace('_', ' ')

		qwant = requests.get('https://api.qwant.com/api/search/images', {'count': '1', 'locale': 'en_en', 'q': nani}, headers={'user-agent': image_ua})

		qwant.raise_for_status()

		qwant = qwant.json()

		if qwant['status'] != 'success':
			raise ValueError(repr(qwant))
	
		imgurl = qwant['data']['result']['items'][0]['media']

		img = requests.get(imgurl, headers={'user-agent': image_ua})

		img.raise_for_status()

		imgdata = io.BytesIO(img.content)

		img = Image.open(imgdata).convert('RGBA')

		img.thumbnail((640,640))

		drawtext(img, what)

		img.save('cache/{}.png'.format(what))

		cached_objects.add(what)


if __name__ == '__main__':

	print('Listening for commands')
	for comment in sub.stream.comments():
		if comment.body.lower().startswith('!reddit'):
			try:
				handle(comment)
			except Exception:
				traceback.print_exc()
	
