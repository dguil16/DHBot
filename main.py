#!/usr/bin/env python

import asyncio
import os
import sys
from os.path import getmtime
import logging
import trivia

import discord

from cleverbot import cleverbot
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

#cleverbot object
clever_bot = cleverbot.Session()

# Initialize client object, begin connection
client = discord.Client()

server_list = []

def yf(func):
   def inner(*args, **kwargs):
      yield from func(*args, **kwargs)
   return inner

# Event handler
@client.async_event
def on_member_join(newmember):
	admin_users = []
	for x in newmember.server.members:
		if bot.check_role(client, x, 'Admin') == True:
			admin_users += [x]
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += " " + (x.mention)
	yield from client.send_message(notification_channel, newmember.name + ' needs permissions. ' + admin_mentions)
	yield from client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible.\n\nIn the meantime, you are free to use the lobby text-chat and Public voice channels. If your Discord username is different from your in game GW2 name, please post in the lobby what your account name is so we can properly identify you. Please be sure to read the announcements as well.\n\nYou may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.\n\nIf you are having difficulties with your sound or voice in Discord, you can check https://support.discordapp.com/hc/en-us or ask in Discord or Guild chat for assistance.')

@client.async_event
def on_message(message):

	if message.content.lower().startswith('!test'):
		yield from client.send_message(message.channel, "Test successful.")

	if bot.check_role(client, message, 'BotBan') == False:

		if message.content.startswith('{}'.format(client.user.mention)):
			cb_message = message.content.partition(' ')[2]
			yield from client.send_message(message.channel, clever_bot.Ask(str(cb_message)))

		if message.content.lower().startswith('!away-set'):
			yield from bot.away_fnc(client, message, 'set')

		if message.content.lower().startswith('!away-return'):
			yield from bot.away_fnc(client, message, 'return')

		if message.content.lower().startswith('!away-whois'):
			yield from bot.away_fnc(client, message, 'whois')

		if message.content.lower() == '!help':
			yield from bot.help(client, message, 'read')

		if message.content.lower() == '!adminhelp':
			yield from bot.help(client, message, 'admin')

		if message.content.lower().startswith('!help '):
			yield from bot.help(client, message, 'info')
	
		if message.content.lower().startswith('!clear'):
			yield from bot.clear(client, message)

		if message.content.lower() == '!events':
			yield from bot.file_interface(client, message, 'events', 'read')

		if message.content.lower().startswith('!events-edit'):
			yield from bot.file_interface(client, message, 'events', 'write')

		if message.content.lower().startswith('!group-create'):
			yield from bot.group(client, message, 'create')

		if message.content.lower().startswith('!group-delete'):
			yield from bot.group(client, message, 'delete')

		if message.content.lower().startswith('!group-enroll'):
			yield from bot.group(client, message, 'enroll')

		if message.content.lower().startswith('!group-add'):
			yield from bot.group(client, message, 'add')

		if message.content.lower().startswith('!group-open'):
			yield from bot.group(client, message, 'open')

		if message.content.lower().startswith('!group-close'):
			yield from bot.group(client, message, 'close')

		if message.content.lower().startswith('!group-call'):
			yield from bot.group(client, message, 'call')

		if message.content.lower().startswith('!group-remove'):
			yield from bot.group(client, message, 'remove')

		if message.content.lower().startswith('!group-unenroll'):
			yield from bot.group(client, message, 'unenroll')

		if message.content.lower().startswith('!group-list'):
			yield from bot.group(client, message, 'list')

		if message.content.lower().startswith('!group-members'):
			yield from bot.group(client, message, 'members')

		if message.content.lower().startswith('!group-info'):
			yield from bot.group(client, message, 'info')

		if message.content.lower().startswith('!hello'):
			yield from bot.greet(client, message)

		if message.content.lower().startswith('!help-edit'):
			yield from bot.help(client, message, 'edit')

		if message.content.lower().startswith('!help-add'):
			yield from bot.help(client, message, 'add')

		if message.content.lower().startswith('!adminhelp-add'):
			yield from bot.help(client, message, 'add-admin')

		if message.content.lower().startswith('!help-delete'):
			yield from bot.help(client, message, 'delete')

		if message.content.lower().startswith('!adminhelp-delete'):
			yield from bot.help(client, message, 'delete-admin')
		
		if message.content.lower().startswith('!lmgtfy'):
			yield from bot.lmgtfy(client, message)

		if message.content.lower().startswith('!mission'):
			yield from bot.mission(client, message)

		if message.content.lower().startswith('!poll-create'):
			yield from poll_module.poll_fnc(client, message, 'create')

		if message.content.lower().startswith('!anonpoll-create'):
			yield from poll_module.poll_fnc(client, message, 'create anon')

		if message.content.lower().startswith('!multipoll-create'):
			yield from poll_module.poll_fnc(client, message, 'create multi')

		if message.content.lower().startswith('!poll-open'):
			yield from poll_module.poll_fnc(client, message, 'open')

		if message.content.lower().startswith('!poll-close'):
			yield from poll_module.poll_fnc(client, message, 'close')

		if message.content.lower().startswith('!poll-info'):
			yield from poll_module.poll_fnc(client, message, 'info')

		if message.content.lower().startswith('!poll-delete'):
			yield from poll_module.poll_fnc(client, message, 'delete')

		if message.content.lower().startswith('!vote '):
			yield from poll_module.poll_fnc(client, message, 'vote')

		if message.content.lower().startswith('!vote-remove'):
			yield from poll_module.poll_fnc(client, message, 'vote remove')

		if message.content.lower().startswith('!vote-change'):
			yield from poll_module.poll_fnc(client, message, 'change')

		if message.content.lower().startswith('!admin-vote'):
			yield from poll_module.poll_fnc(client, message, 'admin')

		if message.content.lower().startswith('!poll-list'):
			yield from poll_module.poll_fnc(client, message, 'list')

		if message.content.lower().startswith('!poll-results'):
			yield from poll_module.poll_fnc(client, message, 'results')

		if message.content.lower().startswith('!survey-create'):
			yield from poll_module.survey_fnc(client, message, 'create')

		if message.content.lower().startswith('!survey-open'):
			yield from poll_module.survey_fnc(client, message, 'open')

		if message.content.lower().startswith('!survey-close'):
			yield from poll_module.survey_fnc(client, message, 'close')

		if message.content.lower().startswith('!survey-info'):
			yield from poll_module.survey_fnc(client, message, 'info')

		if message.content.lower().startswith('!survey-delete'):
			yield from poll_module.survey_fnc(client, message, 'delete')

		if message.content.lower().startswith('!survey-submit'):
			yield from poll_module.survey_fnc(client, message, 'submit')

		if message.content.lower().startswith('!survey-change'):
			yield from poll_module.survey_fnc(client, message, 'change')

		if message.content.lower().startswith('!survey-list'):
			yield from poll_module.survey_fnc(client, message, 'list')

		if message.content.lower().startswith('!survey-results'):
			yield from poll_module.survey_fnc(client, message, 'results')

		if message.content.lower().startswith('!price'):
			yield from bot.price(client, message)

		if message.content.lower().startswith('!purge'):
			yield from bot.purge(client, message)

		if message.content.lower().startswith('!remindme'):
			yield from remind_module.run(client, message)

		#if message.content.lower().startswith('!reminder'):
		#	yield from remind_module.run(client, message, 'public')

		if message.content.lower().startswith('!roster-copy'):
			yield from bot.roster_fnc(client, message, 'copy')

		if message.content.lower().startswith('!roster-formattedcopy'):
			yield from bot.roster_fnc(client, message, 'format')

		if message.content.lower().startswith('!roster-promotion'):
			yield from bot.roster_fnc(client, message, 'promotion')

		if message.content.lower() == '!roster-send':
			yield from bot.roster_fnc(client, message, 'send')

		if message.content.lower().startswith('!roster-sendpromotion'):
			yield from bot.roster_fnc(client, message, 'send promotion')

		if message.content.lower().startswith('!timetohot'):
			yield from bot.time_to_hot(client, message)

		if message.content.lower().startswith('!timetomissions'):
			yield from bot.time_to_missions(client, message)

		if message.content.lower().startswith('!timetoreset'):
			yield from bot.time_to_reset(client, message)

		if message.content.lower().startswith('!timetowvwreset'):
			yield from bot.time_to_wvw_reset(client, message)

		if message.content.lower().startswith('!quit'):
			yield from bot.stop_bot(client, message)

		if message.content.lower().startswith('!roll'):
			yield from bot.roll_dice(client, message)
		
		if message.content.lower().startswith('!wiki'):
			yield from bot.wiki(client, message)

		if message.content.lower().startswith('!trivia'):
			if bot.check_role(client, message, 'Admin') == True or bot.check_role(client, message, 'Trivia Admin') == True:
				yield from trivia_module.trivia_fncs(client, message)
			else:
				yield from client.send_message(message.channel, 'You do not have permission to do that.')

		if message.content.lower() == str(trivia.trivia_answer).lower():
			if message.channel.is_private == True:
				pass
			elif message.channel.name == 'trivia':
				yield from trivia_module.correct_answer(client, message)

		if '(╯°□°）╯︵ ┻━┻' in message.content:
			yield from client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ) \n\n' +str(message.author.name) + ', what did the table do to you?')


@client.async_event
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	global server_list
	server_list = client.servers

#if not client.is_logged_in:
#	print('Logging in to Discord failed')
#	exit(1)

client.run(bot.get_bot_credential('Username'), bot.get_bot_credential('Password'))