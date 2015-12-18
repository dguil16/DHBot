#!/usr/bin/env python

import os
import sys
from os.path import getmtime
import logging
import trivia

import discord

from chatbot import Chatbot
from polls import Poll
from reminder import Reminder
from trivia import Trivia



# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

# Create new instances of bot objects
bot = Chatbot('settings.txt')
remind_module = Reminder()
trivia_module = Trivia()
poll_module = Poll()

# Initialize client object, begin connection
client = discord.Client()
client.login(bot.get_bot_credential('Username'), bot.get_bot_credential('Password'))

if not client.is_logged_in:
	print('Logging in to Discord failed')
	exit(1)

server_list = []

# Event handler
@client.event
def on_member_join(newmember):
	admin_users = []
	for x in newmember.server.members:
		if bot.check_role(client, x, 'Admin') == True:
			admin_users += [x]
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += ' '+str(x.mention())
	client.send_message(notification_channel, newmember.name + ' needs permissions. {}'.format(admin_mentions))
	client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible.\n\nIn the meantime, you are free to use the lobby text-chat and Public voice channels. If your Discord username is different from your in game GW2 name, please post in the lobby what your account name is so we can properly identify you. Please be sure to read the announcements as well.\n\nYou may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.\n\nIf you are having difficulties with your sound or voice in Discord, you can check https://support.discordapp.com/hc/en-us or ask in Discord or Guild chat for assistance.')

@client.event
def on_message(message):
	if bot.check_role(client, message, 'BotBan') == False:

		if message.content == '!help':
			bot.help(client, message, 'read')

		if message.content == '!adminhelp':
			bot.help(client, message, 'admin')

		if message.content.startswith('!help '):
			bot.help(client, message, 'info')
	
		if message.content.startswith('!clear'):
			bot.clear(client, message)

		if message.content == '!events':
			bot.file_interface(client, message, 'events', 'read')

		if message.content.startswith('!events-edit'):
			bot.file_interface(client, message, 'events', 'write')

		if message.content.startswith('!fractal '):
			bot.fractal(client, message, 'send')

		if message.content.startswith('!fractal-add'):
			bot.fractal(client, message, 'add')

		if message.content.startswith('!fractal-remove'):
			bot.fractal(client, message, 'remove')

		if message.content.startswith('!hello'):
			bot.greet(client, message)

		if message.content.startswith('!help-edit'):
			bot.help(client, message, 'edit')

		if message.content.startswith('!help-add'):
			bot.help(client, message, 'add')

		if message.content.startswith('!adminhelp-add'):
			bot.help(client, message, 'add-admin')

		if message.content.startswith('!help-delete'):
			bot.help(client, message, 'delete')

		if message.content.startswith('!adminhelp-delete'):
			bot.help(client, message, 'delete-admin')
		
		if message.content.startswith('!lmgtfy'):
			bot.lmgtfy(client, message)

		if message.content.startswith('!mission'):
			bot.mission(client, message)

		if message.content.startswith('!poll-create'):
			poll_module.poll_fnc(client, message, 'create')

		if message.content.startswith('!anonpoll-create'):
			poll_module.poll_fnc(client, message, 'create anon')

		if message.content.startswith('!multipoll-create'):
			poll_module.poll_fnc(client, message, 'create multi')

		if message.content.startswith('!poll-open'):
			poll_module.poll_fnc(client, message, 'open')

		if message.content.startswith('!poll-close'):
			poll_module.poll_fnc(client, message, 'close')

		if message.content.startswith('!poll-info'):
			poll_module.poll_fnc(client, message, 'info')

		if message.content.startswith('!poll-delete'):
			poll_module.poll_fnc(client, message, 'delete')

		if message.content.startswith('!vote '):
			poll_module.poll_fnc(client, message, 'vote')

		if message.content.startswith('!vote-remove'):
			poll_module.poll_fnc(client, message, 'vote remove')

		if message.content.startswith('!vote-change'):
			poll_module.poll_fnc(client, message, 'change')

		if message.content.startswith('!admin-vote'):
			poll_module.poll_fnc(client, message, 'admin')

		if message.content.startswith('!poll-list'):
			poll_module.poll_fnc(client, message, 'list')

		if message.content.startswith('!poll-results'):
			poll_module.poll_fnc(client, message, 'results')

		if message.content.startswith('!survey-create'):
			poll_module.survey_fnc(client, message, 'create')

		if message.content.startswith('!survey-open'):
			poll_module.survey_fnc(client, message, 'open')

		if message.content.startswith('!survey-close'):
			poll_module.survey_fnc(client, message, 'close')

		if message.content.startswith('!survey-info'):
			poll_module.survey_fnc(client, message, 'info')

		if message.content.startswith('!survey-delete'):
			poll_module.survey_fnc(client, message, 'delete')

		if message.content.startswith('!survey-submit'):
			poll_module.survey_fnc(client, message, 'submit')

		if message.content.startswith('!survey-change'):
			poll_module.survey_fnc(client, message, 'change')

		if message.content.startswith('!survey-list'):
			poll_module.survey_fnc(client, message, 'list')

		if message.content.startswith('!survey-results'):
			poll_module.survey_fnc(client, message, 'results')

		if message.content.startswith('!price'):
			bot.price(client, message)

		if message.content.startswith('!purge'):
			bot.purge(client, message)

		if message.content.startswith('!remindme'):
			remind_module.run(client, message)

		if message.content.startswith('!roster-copy'):
			bot.roster_fnc(client, message, 'copy')

		if message.content.startswith('!roster-formattedcopy'):
			bot.roster_fnc(client, message, 'format')

		if message.content.startswith('!roster-send'):
			bot.roster_fnc(client, message, 'send')

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

		if message.content.startswith('!trivia'):
			if bot.check_role(client, message, 'Admin') == True or bot.check_role(client, message, 'Trivia Admin') == True:
				trivia_module.trivia_fncs(client, message)
			else:
				client.send_message(message.channel, 'You do not have permission to do that.')

		if message.content.lower() == str(trivia.trivia_answer).lower():
			if message.channel.is_private == True:
				pass
			elif message.channel.name == 'trivia':
				trivia_module.correct_answer(client, message)


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
	global server_list
	server_list = client.servers

client.run()

#testing