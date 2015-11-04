#!/usr/bin/env python

import os
import sys
from os.path import getmtime
import logging

import discord

from chatbot import Chatbot



# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

# Create a new instance of a chatbot object
bot = Chatbot('BotCred.txt', 'events.txt', 'help.txt', 'fractal.txt', 'mission.txt')

# Initialize client object, begin connection
client = discord.Client()
client.login(bot.get_bot_credential('Username'), bot.get_bot_credential('Password'))

if not client.is_logged_in:
	print('Logging in to Discord failed')
	exit(1)

# Event handler
@client.event
def on_member_join(newmember):
	admin_users = []
	for x in newmember.server.members:
		if bot.check_role(x, 'Admin') == True:
			admin_users += [x]
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += ' '+str(x.mention())
	client.send_message(notification_channel, newmember.name + ' needs permissions. {}'.format(admin_mentions))
	client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible.\n\nIn the meantime, you are free to use the lobby text-chat and Public voice channels. If your Discord username is different from your in game GW2 name, please post in the lobby what your account name is so we can properly identify you. Please be sure to read the announcements as well.\n\nYou may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.\n\nIf you are having difficulties with your sound or voice in Discord, you can check https://support.discordapp.com/hc/en-us or ask in Discord or Guild chat for assistance.')

@client.event
def on_message(message):
	if bot.check_role(message, 'BotBan') == False:
		if message.content.startswith('!clear'):
			bot.clear(client, message)

		if message.content.startswith('!events'):
			bot.file_interface(client, message, 'events', 'read')

		if message.content.startswith('!edit-events'):
			bot.file_interface(client, message, 'events', 'write')

		if message.content.startswith('!fractal'):
			bot.fractal(client, message, 'send')

		if message.content.startswith('!add-fractal'):
			bot.fractal(client, message, 'add')

		if message.content.startswith('!remove-fractal'):
			bot.fractal(client, message, 'remove')

		if message.content.startswith('!hello'):
			bot.greet(client, message)

		if message.content.startswith('!help'):
			bot.file_interface(client, message, 'help', 'read')

		if message.content.startswith('!edit-help'):
			bot.file_interface(client, message, 'help', 'write')
		
		if message.content.startswith('!lmgtfy'):
			bot.lmgtfy(client, message)

		if message.content.startswith('!mission'):
			bot.mission(client, message)

		if message.content.startswith('!create-poll'):
			bot.poll(client, message, 'create')

		if message.content.startswith('!open-poll'):
			bot.poll(client, message, 'open')

		if message.content.startswith('!close-poll'):
			bot.poll(client, message, 'close')

		if message.content.startswith('!poll-info'):
			bot.poll(client, message, 'info')

		if message.content.startswith('!delete-poll'):
			bot.poll(client, message, 'delete')

		if message.content.startswith('!vote'):
			bot.poll(client, message, 'vote')

		if message.content.startswith('!admin-vote'):
			bot.poll(client, message, 'admin')

		if message.content.startswith('!list-polls'):
			bot.poll(client, message, 'list')

		if message.content.startswith('!poll-results'):
			bot.poll(client, message, 'results')

		if message.content.startswith('!price'):
			bot.price(client, message)

		if message.content.startswith('!purge'):
			bot.purge(client, message)

#		if message.content.startswith('!remindme'):
#			bot.reminder(client, message)

		if message.content.startswith('!timetoraid'):
			pass

		if message.content.startswith('!timetohot'):
			bot.time_to_hot(client, message)

		if message.content.startswith('!timetomissions'):
			bot.time_to_missions(client, message)

		if message.content.startswith('!timetoreset'):
			bot.time_to_reset(client, message)

		if message.content.startswith('!timetowvwreset'):
			bot.time_to_wvw_reset(client, message)

		if message.content.startswith('!quit'):
			bot.stop_bot(client, message)

		if message.content.startswith('!roll'):
			bot.roll_dice(client, message)
		
		if message.content.startswith('!wiki'):
			bot.wiki(client, message)

# This will have to wait until the new gw2 api, which should contain this information.
#		if message.content.startswith('!worldbosses'):
#			pass

		if '(╯°□°）╯︵ ┻━┻' in message.content:
			client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ) \n\n' +str(message.author.name) + ', what did the table do to you?')


@client.event
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run()

#testing