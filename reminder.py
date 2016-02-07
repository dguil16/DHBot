import asyncio
import datetime
import json
import threading

import discord

from chatbot import Chatbot

class Reminder(object):
	"""
	Messages should have the format
	!remindme HH MM <text>
	"""
	def __init__(self):
		pass

	async def respond(self, client, message, bot, text):
		await client.send_message(message.author, 'Reminder: ' + text)

	async def run(self, client, message, bot, query):
		with open('reminders.txt', 'r') as f:
			reminders_json = json.load(f)
		if query == 'self' or query == 'channel':
			hours = int(message.content.split(' ', 3)[1])
			minutes = float(message.content.split(' ', 3)[2])
			text = message.content.split(' ', 3)[3]

			seconds = hours*60*60 + minutes*60

			now = datetime.datetime.utcnow()
			sched_time = now + datetime.timedelta(seconds = seconds)
			reminders_json[str(sched_time)] = {"author": message.author.id, "channel": message.channel.id, "type": query, "text": text}

			await client.send_message(message.channel, 'Reminder set.')
			await asyncio.sleep(seconds)
			if query == 'self':
				await client.send_message(message.author, 'Reminder: ' + text)
			if query == 'channel':
				await client.send_message(message.channel, 'Reminder: ' + text)

		if query == 'group':
			''' format is !remind-group <group>; HH MM <message>'''

			grp = message.content.partition('; ')[0].partition(' ')[2]
			hours = int(message.content.partition('; ')[2].split(' ', 2)[0])
			minutes = float(message.content.partition('; ')[2].split(' ', 2)[1])
			text = message.content.partition('; ')[2].split(' ', 2)[2]

			seconds = hours*60*60 + minutes*60

			await client.send_message(message.channel, 'Reminder set.')
			message.content = '!group-call {}'.format(grp)
			await asyncio.sleep(seconds)
			await bot.group(client, message, 'call')
			await client.send_message(message.channel, "Reminder: {}".format(text))
		#with open('reminders.txt', 'w') as f:
		#	f.write(str(json.dumps(reminders_json)))
		#needs to be relocated to work properly
		#t = threading.Timer(seconds, self.respond, [client, message, text])
		#t.start()