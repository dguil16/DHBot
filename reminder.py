import threading

import discord

class Reminder(object):
	"""
	Messages should have the format
	!remindme HH MM <text>
	"""
	def __init__(self):
		pass

	async def respond(self, client, message, text):
		await client.send_message(message.author, 'Reminder: ' + text)

	async def run(self, client, message):
		hours = int(message.content.split(' ', 3)[1])
		minutes = int(message.content.split(' ', 3)[2])
		text = message.content.split(' ', 3)[3]

		seconds = hours*60*60 + minutes*60

		await client.send_message(message.channel, 'Reminder set.')

		t = threading.Timer(seconds, self.respond, [client, message, text])
		t.start()