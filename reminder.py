import threading

import discord

class Reminder(object):
	"""
	Messages should have the format
	!remindme HH MM <text>
	"""
	def __init__(self):
		pass

	def respond(self, client, message, text):
		client.send_message(message.channel, '@' + message.author.name + ' ' + text)

	def run(self, client, message):
		hours = int(message.content.split(' ', 3)[1])
		minutes = int(message.content.split(' ', 3)[2])
		text = message.content.split(' ', 3)[3]

		seconds = hours*60*60 + minutes*60

		t = threading.Timer(seconds, self.respond(client, message, text))
		t.start()