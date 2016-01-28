#!/usr/bin/env python

import asyncio
import json
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

# Event handler
@client.event
async def on_member_join(newmember):
	admin_users = []
	for x in newmember.server.members:
		if bot.check_role(client, x, 'Admin') == True:
			admin_users += [x]
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += " " + (x.mention)
	await client.send_message(notification_channel, newmember.name + ' needs permissions. ' + admin_mentions)
	await client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible.\n\nIn the meantime, you are free to use the lobby text-chat and Public voice channels. If your Discord username is different from your in game GW2 name, please post in the lobby what your account name is so we can properly identify you. Please be sure to read the announcements as well.\n\nYou may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.\n\nIf you are having difficulties with your sound or voice in Discord, you can check https://support.discordapp.com/hc/en-us or ask in Discord or Guild chat for assistance.')

@client.event
async def on_member_update(before, after):
	if str(before.status) == 'offline' and str(after.status) == 'online' and bot.check_role(client, after, "Member") == True:
			x = open("display_names.txt", 'r')
			disp_names = json.load(x)
			x.close()
			if after.id not in disp_names:
				await client.send_message(after, "Your GW2 Display Name is not listed in our database. Please enter `!displayname <GW2 Display name>` (without <>) in Discord. Be sure to use your full name, including the 4 digits at the end. If you need help, please ask an Admin.")

	if str(before.status) == 'offline' and str(after.status) == 'online' and after.name == "Scottzilla":
		await client.send_message(after, ":boom: Happy birthday! :boom:")

@client.event
async def on_message(message):

#	if message.content.lower().startswith('!test'):
#		await client.send_message(message.channel, "Test successful.")

	if message.content == "!groupupdate":
		await bot.groupupdate(client, message)

	if bot.check_role(client, message, 'BotBan') == False:

		if message.content.startswith('{}'.format(client.user.mention)):
			cb_message = message.content.partition(' ')[2]
			answer = clever_bot.Ask(str(cb_message))
			await client.send_message(message.channel, str(answer))

		if message.content.lower().startswith('!away-set'):
			await bot.away_fnc(client, message, 'set')

		if message.content.lower().startswith('!away-return'):
			await bot.away_fnc(client, message, 'return')

		if message.content.lower().startswith('!away-whois'):
			await bot.away_fnc(client, message, 'whois')

		if message.content.lower() == '!help':
			await bot.help(client, message, 'read')

		if message.content.lower() == '!adminhelp':
			await bot.help(client, message, 'admin')

		if message.content.lower().startswith('!help '):
			await bot.help(client, message, 'info')
	
		if message.content.lower().startswith('!clear'):
			await bot.clear(client, message)

		if message.content.lower().startswith('!displayname '):
			await bot.displayname(client, message, 'self')

		if message.content.lower().startswith('!displayname-send'):
			await bot.displayname(client, message, 'send')

		if message.content.lower().startswith('!displayname-set '):
			await bot.displayname(client, message, 'set')

		if message.content.lower() == '!events':
			await bot.file_interface(client, message, 'events', 'read')

		if message.content.lower().startswith('!events-edit'):
			await bot.file_interface(client, message, 'events', 'write')

		if message.content.lower().startswith('!group-create'):
			await bot.group(client, message, 'create')

		if message.content.lower().startswith('!group-delete'):
			await bot.group(client, message, 'delete')

		if message.content.lower().startswith('!group-enroll'):
			await bot.group(client, message, 'enroll')

		if message.content.lower().startswith('!group-add '):
			await bot.group(client, message, 'add')

		if message.content.lower().startswith('!group-add_id'):
			await bot.group(client, message, 'add_id')

		if message.content.lower().startswith('!group-open'):
			await bot.group(client, message, 'open')

		if message.content.lower().startswith('!group-close'):
			await bot.group(client, message, 'close')

		if message.content.lower().startswith('!group-call'):
			await bot.group(client, message, 'call')

		if message.content.lower().startswith('!group-remove '):
			await bot.group(client, message, 'remove')

		if message.content.lower().startswith('!group-remove_id '):
			await bot.group(client, message, 'remove')

		if message.content.lower().startswith('!group-unenroll'):
			await bot.group(client, message, 'unenroll')

		if message.content.lower().startswith('!group-list'):
			await bot.group(client, message, 'list')

		if message.content.lower().startswith('!group-members'):
			await bot.group(client, message, 'members')

		if message.content.lower().startswith('!group-info'):
			await bot.group(client, message, 'info')

		if message.content.lower().startswith('!hello'):
			await bot.greet(client, message)

		if message.content.lower().startswith('!help-edit'):
			await bot.help(client, message, 'edit')

		if message.content.lower().startswith('!help-add'):
			await bot.help(client, message, 'add')

		if message.content.lower().startswith('!adminhelp-add'):
			await bot.help(client, message, 'add-admin')

		if message.content.lower().startswith('!help-delete'):
			await bot.help(client, message, 'delete')

		if message.content.lower().startswith('!adminhelp-delete'):
			await bot.help(client, message, 'delete-admin')
		
		if message.content.lower().startswith('!lmgtfy'):
			await bot.lmgtfy(client, message)

		if message.content.lower().startswith('!mission'):
			await bot.mission(client, message)

		if message.content.lower().startswith('!poll-create'):
			await poll_module.poll_fnc(client, message, 'create')

		if message.content.lower().startswith('!anonpoll-create'):
			await poll_module.poll_fnc(client, message, 'create anon')

		if message.content.lower().startswith('!multipoll-create'):
			await poll_module.poll_fnc(client, message, 'create multi')

		if message.content.lower().startswith('!poll-open'):
			await poll_module.poll_fnc(client, message, 'open')

		if message.content.lower().startswith('!poll-close'):
			await poll_module.poll_fnc(client, message, 'close')

		if message.content.lower().startswith('!poll-info'):
			await poll_module.poll_fnc(client, message, 'info')

		if message.content.lower().startswith('!poll-delete'):
			await poll_module.poll_fnc(client, message, 'delete')

		if message.content.lower().startswith('!vote '):
			await poll_module.poll_fnc(client, message, 'vote')

		if message.content.lower().startswith('!vote-remove'):
			await poll_module.poll_fnc(client, message, 'vote remove')

		if message.content.lower().startswith('!vote-change'):
			await poll_module.poll_fnc(client, message, 'change')

		if message.content.lower().startswith('!admin-vote'):
			await poll_module.poll_fnc(client, message, 'admin')

		if message.content.lower().startswith('!poll-list'):
			await poll_module.poll_fnc(client, message, 'list')

		if message.content.lower().startswith('!poll-results'):
			await poll_module.poll_fnc(client, message, 'results')

		if message.content.lower().startswith('!survey-create'):
			await poll_module.survey_fnc(client, message, 'create')

		if message.content.lower().startswith('!survey-open'):
			await poll_module.survey_fnc(client, message, 'open')

		if message.content.lower().startswith('!survey-close'):
			await poll_module.survey_fnc(client, message, 'close')

		if message.content.lower().startswith('!survey-info'):
			await poll_module.survey_fnc(client, message, 'info')

		if message.content.lower().startswith('!survey-delete'):
			await poll_module.survey_fnc(client, message, 'delete')

		if message.content.lower().startswith('!survey-submit'):
			await poll_module.survey_fnc(client, message, 'submit')

		if message.content.lower().startswith('!survey-change'):
			await poll_module.survey_fnc(client, message, 'change')

		if message.content.lower().startswith('!survey-list'):
			await poll_module.survey_fnc(client, message, 'list')

		if message.content.lower().startswith('!survey-results'):
			await poll_module.survey_fnc(client, message, 'results')

		if message.content.lower().startswith('!price'):
			await bot.price(client, message)

		if message.content.lower().startswith('!purge'):
			await bot.purge(client, message)

		if message.content.lower().startswith('!remindme'):
			await remind_module.run(client, message)

		#if message.content.lower().startswith('!reminder'):
		#	await remind_module.run(client, message, 'public')

		if message.content.lower().startswith('!roster-copy'):
			await bot.roster_fnc(client, message, 'copy')

		if message.content.lower().startswith('!roster-formattedcopy'):
			await bot.roster_fnc(client, message, 'format')

		if message.content.lower().startswith('!roster-promotion'):
			await bot.roster_fnc(client, message, 'promotion')

		if message.content.lower() == '!roster-send':
			await bot.roster_fnc(client, message, 'send')

		if message.content.lower().startswith('!roster-sendpromotion'):
			await bot.roster_fnc(client, message, 'send promotion')

		if message.content.lower().startswith('!timetohot'):
			await bot.time_to_hot(client, message)

		if message.content.lower().startswith('!timetomissions'):
			await bot.time_to_missions(client, message)

		if message.content.lower().startswith('!timetoreset'):
			await bot.time_to_reset(client, message)

		if message.content.lower().startswith('!timetowvwreset'):
			await bot.time_to_wvw_reset(client, message)

		if message.content.lower().startswith('!quit'):
			await bot.stop_bot(client, message)

		if message.content.lower().startswith('!roll'):
			await bot.roll_dice(client, message)

		if message.content.lower() == '!whatismyid':
			await bot.id_fnc(client, message, 'self')

		if message.content.lower().startswith('!checkid'):
			await bot.id_fnc(client, message, 'other')
		
		if message.content.lower().startswith('!wiki'):
			await bot.wiki(client, message)

		if message.content.lower().startswith('!trivia'):
			if bot.check_role(client, message, 'Admin') == True or bot.check_role(client, message, 'Trivia Admin') == True:
				await trivia_module.trivia_fncs(client, message)
			else:
				await client.send_message(message.channel, 'You do not have permission to do that.')

		if message.content.lower() == str(trivia.trivia_answer).lower():
			if message.channel.is_private == True:
				pass
			elif message.channel.name == 'trivia':
				await trivia_module.correct_answer(client, message)

		if '(╯°□°）╯︵ ┻━┻' in message.content:
			await client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ) \n\n' +str(message.author.name) + ', what did the table do to you?')


@client.event
async def on_ready():
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