#!/usr/bin/env python

import asyncio
import datetime
from datetime import datetime
import fractals
import json
import os
import requests
import sys
from os.path import getmtime
import logging
import trivia

import discord

from cleverbot import cleverbot
from chatbot import Chatbot
from polls import Poll
from reminder import Reminder
from timezone import Timezone
from trivia import Trivia

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

# Create new instances of bot objects
bot = Chatbot('settings.txt')
remind_module = Reminder()
timezone_module = Timezone()
trivia_module = Trivia()
poll_module = Poll()

# RPi Lighting
if bot.gpio_enabled == "yes":
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	statPin = 4
	GPIO.setup(statPin, GPIO.OUT)

#cleverbot object
clever_bot = cleverbot.Session()

# Initialize client object, begin connection
client = discord.Client()

serv = ''

# Event handler
@client.event
async def on_member_join(newmember):
	admin_users = []
	leadership_names = []
	for x in newmember.server.members:
		if bot.check_role(client, x, 'Admin') == True:
			admin_users += [x]
		if bot.check_role(client, x, 'Leadership') == True:
			leadership_names += [x.name]
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	if notification_channel == None:
		await client.create_channel(serv, 'bot-notifications')
		notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += " " + (x.mention)
	await client.send_message(notification_channel, "{} needs permissions. {}".format(newmember.mention, admin_mentions))
	await client.send_message(newmember, 'Welcome to the Discord server for Descendants of Honor. My name is Xantha, the chat bot for this server. If you are a member of DH or intend to join our guild in the future, please respond to this message with the following to verify that you are a member so that you can automatically receive the appropriate permissions for Discord:\n`!api <Your GW2 API key>`, without the <>. This API key only needs the \"Account\" permissions. For example:\n`!api AG6BE513-0890-A640-97D9-708A7594593781E9803C-F348-48B4-9A70-CE0B45072778`\n\nIf you are unfamiliar with this process, do the following:\n\n1) Go to https://account.arena.net/\n2) Click on \"Applications\" at the upper right.\n3) Click \"New Key\" on the right.\n4) Name the key whatever you would like and ensure the \"account\" checkbox is checked. You do not need to check any other boxes.\n5) Click \"Generate API Key\"\n\nThe information this makes available is the following: your GW2 display name, the world you belong to, if you are a commander, what guilds you are in, when your account was created, if you have a commander tag, and if your account is a free account, a GW2 account, or a HoT account. The only information that we will store is your display name, and you are welcome to delete this API key after you submit it.\n:exclamation: Submitting this is required for DH members.\n\nIf you are not a DH member, you may still submit this information so that we may know who you are in game, but it will not automatically assign you permissions. You will need to contact Alethia or Xorin, or have another member give you guest permissions. In the mean time, you are welcome to use the lobby text channel or Public voice channel.\n\nIf you are having difficulties with your sound or voice in Discord, you can check https://support.discordapp.com/hc/en-us or ask in Discord or guild chat for assistance. If you encounter any problems with the bot, please contact Xorin.')

	if newmember.name in leadership_names:
		await client.send_message(newmember, "I have noticed that your name matches the name of one of our members of leadership. Please take a moment to go to your Discord settings (the cog on the lower left of the client) and change your username. If you need assistance with this, please ask. Failure to make this change may result in your Discord permissions being revoked.")
		await client.send_message(notification_channel, "The new member with user ID {} currently has the same name as {}. They have been asked to change their name.".format(newmember.id, newmember.name))

@client.event
async def on_member_update(before, after):
	notification_channel = discord.utils.find(lambda m: m.name == 'bot-notifications', after.server.channels)

	if (str(before.status) == 'offline' and str(after.status) == 'online') or ((str(before.status) == 'online' or str(before.status) == 'idle') and str(after.status) == 'offline'):
		try:
			with open('discord_logs.txt', 'r') as f:
				discord_logs = json.load(f)
		except:
			discord_logs = json.loads('{}')
		if after.id not in discord_logs:
			discord_logs[after.id] = {"last login": "N/A", "last logoff": "N/A"}
		now = str(datetime.utcnow())
		if str(after.status) == 'online':
			discord_logs[after.id]['last login'] = now
		if str(after.status) == 'offline':
			discord_logs[after.id]['last logoff'] = now
		with open('discord_logs.txt', 'w') as f:
			f.write(json.dumps(discord_logs))
	
	if str(before.status) == 'offline' and str(after.status) == 'online' and bot.check_role(client, after, "Member") == True:
			x = open("display_names.txt", 'r')
			disp_names = json.load(x)
			x.close()
			if after.id not in disp_names and KT_role not in after.roles:
				await client.send_message(after, "My name is Xantha, the DH Discord bot. According to my records, your GW2 Display Name is not listed in our database. Please enter \n`!api <GW2 API>`\n without the <>. This API key only needs the \"Account\" permissions. For example:\n`!api AG6BE513-0890-A640-97D9-708A7594593781E9803C-F348-48B4-9A70-CE0B45072778`\n\nIf you are unfamiliar with this process, do the following:\n\n1) Go to https://account.arena.net/\n2) Click on \"Applications\" at the upper right.\n3) Click \"New Key\" on the right.\n4) Name the key whatever you would like and ensure the \"account\" checkbox is checked. You do not need to check any other boxes.\n5) Click \"Generate API Key\"\n\nThe information this makes available is the following: your GW2 display name, the world you belong to, if you are a commander, what guilds you are in, when your account was created, if you have a commander tag, and if your account is a free account, a GW2 account, or a HoT account. The only information that we will store is your display name, and you are welcome to delete this API key after you submit it.")

	leadership_names = []
	for x in after.server.members:
		if bot.check_role(client, x, 'Leadership') == True:
			leadership_names += [x.name]
	if before.name not in leadership_names and after.name in leadership_names and bot.check_role(client, after, "Leadership") == False:
		await client.send_message(after, "I have noticed that you have changed your name to the name of one of our members of leadership. Please take a moment to go to your Discord settings and change your username to something else. Failure to make this change may result in your Discord permissions being revoked.")
		await client.send_message(notification_channel, "The member with user ID {} has changed their name from {} to {}. They have been asked to change their name.".format(after.id, before.name, after.name))
	if before.name in leadership_names and after.name not in leadership_names and bot.check_role(client, after, "Leadership") == False:
		await client.send_message(after, "Thank you for changing your username.")
		await client.send_message(notification_channel, "The member with user ID {} has changed their name from {} to {}.".format(after.id, before.name, after.name))

	if str(before.status) == 'offline' and str(after.status) == 'online' and after.name == "Scottzilla":
		await client.send_message(after, ":boom: Happy birthday! :boom:")

	if str(before.status) != str(after.status):
		member = discord.utils.find(lambda m: m.id == after.id, serv.members)
		with open('display_names.txt', 'r') as f:
			display_names = json.load(f)
		last_update_raw = os.path.getmtime('jsonroster.txt')
		last_update = datetime.fromtimestamp(last_update_raw)
		update_time = datetime.now() - last_update
		if update_time.total_seconds() > 900: #15 minutes = 900 seconds
			bot.roster_update(client)
		with open('jsonroster.txt', 'r') as f:
			raw_roster = json.load(f)

		if member.id in display_names:
			name = display_names[str(member.id)]["display name"]
			if name in raw_roster:
				rank = raw_roster[name]["rank"]
			else:
				rank = "None"
			role_name_list = []
			for x in member.roles:
				role_name_list += [x.name]
			member_role = discord.utils.find(lambda m: m.name == "Member", serv.roles)
			rank_list = ["War Council", "Elder", "Knight Warden", "Knight", "Squire", "Applicant", "Ambassador", "Guests"]
			if rank == "None" and bot.check_role(client, member, "Commander") == False:
				if "Member" in role_name_list:
					for x in role_name_list:
						if x in rank_list:
							old_rank = x
					old_rank_role = discord.utils.find(lambda m: m.name == old_rank, serv.roles)
					roles_to_remove = [old_rank_role, member_role]
					await client.remove_roles(member, old_rank_role)
					await asyncio.sleep(2)
					await client.remove_roles(member, member_role)
					await asyncio.sleep(2)
					guest_role = discord.utils.find(lambda m: m.name == "Guest", serv.roles)
					await client.add_roles(member, guest_role)
					await client.send_message(notification_channel, "{} is no longer a member of the guild and has been given the Guest rank. Removed {} and {} roles.".format(member.name, member_role.name, old_rank_role.name))

			elif rank != "Commander" and rank != "None" and bot.check_role(client, member, "Commander") == False:
				if rank not in role_name_list:
					for x in role_name_list:
						if x in rank_list:
							old_rank = x
					old_rank_role = discord.utils.find(lambda m: m.name == old_rank, serv.roles)
					await client.remove_roles(member, old_rank_role)
					await asyncio.sleep(1)
					rank_role = discord.utils.find(lambda m: m.name == rank, serv.roles)
					await client.add_roles(member, rank_role)
					await client.send_message(notification_channel, "{}'s rank changed from {} to {}.".format(member.name, old_rank_role.name, rank_role.name))
			

@client.event
async def on_message(message):

	if bot.check_role(client, message, 'BotBan') == False:

		if bot.gpio_enabled == "yes":
			GPIO.output(statPin,1)

		if message.content.lower().startswith('!'): 
			await client.send_typing(message.channel)
		
	#		if message.content.lower() == '!test':
	#			await client.send_message(message.channel, serv.name)

	#		if message.content.lower().startswith('!play'):
	#			await bot.play(client, message, serv)

	#		if message.content.lower() == '!stop':
	#			await voice.disconnect()

			if message.content.lower() == "!achiev_list-update":
				if bot.check_role(client, message, 'Admin') == True:
					await client.send_typing(message.channel)
					achiev_data = []
					response = requests.get("https://api.guildwars2.com/v2/achievements")
					achiev_list = json.loads(response.text)
					iterations = (len(achiev_list) + 199) // 200
					remainder = len(achiev_list) % 200
					x=0
					while x < iterations-1:
						i = 1
						id_list = ""
						while i <= 200:
							id_list = id_list + str(achiev_list[i+200*x]) + ","
							i = i+1
						id_list = id_list[:-1]
						response =  requests.get("https://api.guildwars2.com/v2/achievements?ids="+id_list)
						achiev_data = achiev_data + json.loads(response.text)
						x = x+1
					id_list = ""
					i=1
					while i < len(achiev_list) % 200:
						id_list = id_list + str(achiev_list[i + 200*(iterations-1)]) + ","
						i = i+1
					id_list = id_list[:-1]
					response =  requests.get("https://api.guildwars2.com/v2/achievements?ids="+id_list)
					achiev_data = achiev_data + json.loads(response.text)
					with open("achievement_data.txt", 'w') as f:
						f.write(str(json.dumps(achiev_data)))
					await client.send_message(message.channel, "The achievement database has been updated.")

	#		if message.content.startswith('{}'.format(client.user.mention)):
	#			cb_message = message.content.partition(' ')[2]
	#			answer = clever_bot.Ask(str(cb_message))
	#			await client.send_message(message.channel, str(answer))

			elif message.content.lower().startswith('!api '):
				await bot.api(client, message, serv)

			elif message.content.lower().startswith('!away-return'):
				await bot.away_fnc(client, message, 'return')

			elif message.content.lower().startswith('!away-set'):
				await bot.away_fnc(client, message, 'set')

			elif message.content.lower().startswith('!away-whois'):
				await bot.away_fnc(client, message, 'whois')

			elif message.content.lower().startswith('!checkid'):
				await bot.id_fnc(client, message, 'other')
		
			elif message.content.lower().startswith('!clear'):
				await bot.clear(client, message)

			elif message.content.lower().startswith('!displayname-send'):
				await bot.displayname(client, message, 'send')

			elif message.content.lower().startswith('!displayname-set '):
				await bot.displayname(client, message, 'set')

			elif message.content.lower() == '!events':
				await bot.file_interface(client, message, 'events', 'read')

			elif message.content.lower().startswith('!events-edit'):
				await bot.file_interface(client, message, 'events', 'write')

			elif message.content.lower().startswith('!fractals '):
				try:
					kind = message.content.lower().split(" ")[1]
					info = message.content.lower().partition(" ")[2].partition(" ")[2]
					call_details = await fractals.call(client, message, kind, info)
					candidate_mentions = ""
					if call_details == False:
						await client.send_message(message.channel, "I did not understand your request. Currently I only support Level requests, e.g.: !fractals level 50")
					elif call_details["candidates"] == []:
						await client.send_message(message.channel, "There were no users found who meet the specified request.")
					else:
						candidates = call_details["candidates"]
						message_content = call_details["message"]
						for x in candidates:
							candidate_mentions = candidate_mentions + str(bot.member_lookup(client, x, serv).mention) + ", "
						candidate_mentions = candidate_mentions[:-2]
						await client.send_message(message.channel, "{} {} {}".format(message.author.mention, message_content, candidate_mentions))
				except: await client.send_message(message.channel, "I did not recognize what kind of Fractal you were trying to request. Please try again.")


			elif message.content.lower().startswith('!fractal-enroll '):
				API_key = message.content.partition(' ')[2]
				await fractals.enroll(client, message, message.author.id, API_key)

			elif message.content.lower() == "!fractal-unenroll":
				await fractals.unenroll(client, message, message.author.id)

			elif message.content.lower().startswith('!group-create'):
				await bot.group(client, message, 'create')

			elif message.content.lower().startswith('!group-delete'):
				await bot.group(client, message, 'delete')

			elif message.content.lower().startswith('!group-enroll'):
				await bot.group(client, message, 'enroll')

			elif message.content.lower().startswith('!group-add '):
				await bot.group(client, message, 'add')

			elif message.content.lower().startswith('!group-open'):
				await bot.group(client, message, 'open')

			elif message.content.lower().startswith('!group-close'):
				await bot.group(client, message, 'close')

			elif message.content.lower().startswith('!group-call'):
				await bot.group(client, message, 'call')

			elif message.content.lower().startswith('!group-mine'):
				await bot.group(client, message, 'mine')

			elif message.content.lower().startswith('!group-remove '):
				await bot.group(client, message, 'remove')

			elif message.content.lower().startswith('!group-remove_all '):
				await bot.group(client, message, 'remove all')

			elif message.content.lower().startswith('!group-unenroll'):
				await bot.group(client, message, 'unenroll')

			elif message.content.lower().startswith('!group-list'):
				await bot.group(client, message, 'list')

			elif message.content.lower().startswith('!group-members'):
				await bot.group(client, message, 'members')

			elif message.content.lower().startswith('!group-info'):
				await bot.group(client, message, 'info')

			elif message.content.lower().startswith('!guest'):
				await bot.guest(client, message, serv)

			elif message.content.lower().startswith('!hello'):
				await bot.greet(client, message)

			elif message.content.lower().startswith('!help'):
				await client.send_message(message.channel, "You can find a list of commands I understand, their syntax, and brief explanation in the following document: https://goo.gl/80heLg")

			elif message.content.lower().startswith('!last_on '):
				id_or_name = message.content.partition(' ')[2]
				member = bot.member_lookup(client, id_or_name, serv)
				if member != None:
					last_on = bot.log_fnc(member, 'last on')
					await client.send_message(message.channel, "{} was last seen online: {}.".format(member.name, str(last_on).partition('.')[0]))
				else:
					await client.send_message(message.channel, "There was an error finding the member {}. There may be multiple or no members with that name/ID.".format(id_or_name))

			elif message.content.lower().startswith('!lmgtfy'):
				await bot.lmgtfy(client, message)

			elif message.content.lower().startswith('!mission '):
				await bot.mission(client, message, 'info')

			elif message.content.lower().startswith('!mission-add'):
				await bot.mission(client, message, 'add')

			elif message.content.lower().startswith('!mission-edit'):
				await bot.mission(client, message, 'edit')

			elif message.content.lower().startswith('!mission-delete'):
				await bot.mission(client, message, 'delete')

			elif message.content.lower().startswith('!mission-list'):
				await bot.mission(client, message, 'list')

			elif message.content.lower().startswith('!poll-close'):
				await poll_module.poll_fnc(client, message, 'close')

			elif message.content.lower().startswith('!poll-create '):
				await poll_module.poll_fnc(client, message, 'create')

			elif message.content.lower().startswith('!poll-create_anon'):
				await poll_module.poll_fnc(client, message, 'create anon')

			elif message.content.lower().startswith('!poll-create_multi'):
				await poll_module.poll_fnc(client, message, 'create multi')

			elif message.content.lower().startswith('!poll-delete'):
				await poll_module.poll_fnc(client, message, 'delete')

			elif message.content.lower().startswith('!poll-info'):
				await poll_module.poll_fnc(client, message, 'info')

			elif message.content.lower().startswith('!poll-list'):
				await poll_module.poll_fnc(client, message, 'list')

			elif message.content.lower().startswith('!poll-open'):
				await poll_module.poll_fnc(client, message, 'open')

			elif message.content.lower().startswith('!poll-results'):
				await poll_module.poll_fnc(client, message, 'results')

			elif message.content.lower().startswith('!price'):
				await bot.price(client, message)

			elif message.content.lower().startswith('!purge'):
				await bot.purge(client, message)

			elif message.content.lower().startswith('!quit'):
				await bot.stop_bot(client, message)

			elif message.content.lower().startswith('!rank-update'):
				if bot.check_role(client, message, 'Admin') == True:
					await bot.rank_update(client, message, serv)
				else:
					await client.send_message(message.channel, 'You do not have permission to use this function.')

			elif message.content.lower().startswith('!remindme'):
				await remind_module.run(client, message, bot)

			elif message.content.lower().startswith('!food'):
				await client.send_message(message.channel, "Timer started.")
				await asyncio.sleep(1500) #25 minutes = 1500
				await client.send_message(message.channel, "Food check!")

			elif message.content.lower().startswith('!reminder'):
				await remind_module.channel(client, message, bot)

			elif message.content.lower().startswith('!remind-group'):
				await remind_module.group(client, message, bot)

			elif message.content.lower().startswith('!tz'):
				await timezone_module.setTimeZone(client, message)

			elif message.content.lower().startswith('!role-assign'):
				member_id_or_name = message.content.partition(' ')[2].partition('; ')[0]
				role_names = message.content.partition(' ')[2].partition('; ')[2].split(', ')
				await bot.role_fnc(client, message.author, message.channel, member_id_or_name, role_names, 'assign')

			elif message.content.lower().startswith('!role-remove'):
				member_id_or_name = message.content.partition(' ')[2].partition('; ')[0]
				role_names = message.content.partition(' ')[2].partition('; ')[2].split(', ')
				await bot.role_fnc(client, message.author, message.channel, member_id_or_name, role_names, 'remove')

			elif message.content.lower().startswith('!roll'):
				await bot.roll_dice(client, message)

			elif message.content.lower().startswith('!roster-copy'):
				await bot.roster_fnc(client, message, 'copy')

			elif message.content.lower() == "!roster-last_on":
				await bot.roster_fnc(client, message, 'last on')

			elif message.content.lower().startswith('!roster-promotion'):
				await bot.roster_fnc(client, message, 'promotion')

			elif message.content.lower() == '!roster-send':
				await bot.roster_fnc(client, message, 'send')

			elif message.content.lower().startswith('!roster-send '):
				await bot.roster_fnc(client, message, 'send specified')

			elif message.content.lower().startswith('!roster-sendpromotion'):
				await bot.roster_fnc(client, message, 'send promotion')

			elif message.content.lower().startswith('!roster-update') and bot.check_role(client, message, "Admin") == True:
				bot.roster_update(client)
				await client.send_message(message.channel, "The roster database has been updated.")

			elif message.content.lower().startswith('!survey-change'):
				await poll_module.survey_fnc(client, message, 'change')

			elif message.content.lower().startswith('!survey-close'):
				await poll_module.survey_fnc(client, message, 'close')

			elif message.content.lower().startswith('!survey-create'):
				await poll_module.survey_fnc(client, message, 'create')

			elif message.content.lower().startswith('!survey-delete'):
				await poll_module.survey_fnc(client, message, 'delete')

			elif message.content.lower().startswith('!survey-info'):
				await poll_module.survey_fnc(client, message, 'info')

			elif message.content.lower().startswith('!survey-list'):
				await poll_module.survey_fnc(client, message, 'list')

			elif message.content.lower().startswith('!survey-open'):
				await poll_module.survey_fnc(client, message, 'open')

			elif message.content.lower().startswith('!survey-results'):
				await poll_module.survey_fnc(client, message, 'results')

			elif message.content.lower().startswith('!survey-submit'):
				await poll_module.survey_fnc(client, message, 'submit')

			elif message.content.lower().startswith('!timetomissions'):
				await bot.time_to_missions(client, message)

			elif message.content.lower().startswith('!timetoreset'):
				await bot.time_to_reset(client, message)

			elif message.content.lower().startswith('!timetowvwreset'):
				await bot.time_to_wvw_reset(client, message)

			elif message.content.lower().startswith('!vote '):
				await poll_module.poll_fnc(client, message, 'vote')

			elif message.content.lower().startswith('!vote-admin'):
				await poll_module.poll_fnc(client, message, 'admin')

			elif message.content.lower().startswith('!vote-change'):
				await poll_module.poll_fnc(client, message, 'change')

			elif message.content.lower().startswith('!vote-remove'):
				await poll_module.poll_fnc(client, message, 'vote remove')

			elif message.content.lower() == '!whatismyid':
				await bot.id_fnc(client, message, 'self')

			elif message.content.lower().startswith('!wiki'):
				await bot.wiki(client, message)

			elif message.content.lower().startswith('!trivia'):
				if bot.check_role(client, message, 'Admin') == True or bot.check_role(client, message, 'Trivia Admin') == True:
					await trivia_module.trivia_fncs(client, message)
				else:
					await client.send_message(message.channel, 'You do not have permission to do that.')

			else: await client.send_message(message.channel, "I did not understand your command. Please try again.")

		if message.content.lower() == str(trivia.trivia_answer).lower():
			if message.channel.is_private == True:
				pass
			elif message.channel.name == 'trivia':
				await trivia_module.correct_answer(client, message)

		if '(?°?°)?? ???' in message.content:
			await client.send_message(message.channel, '---? ?( ?-??) \n\n' +str(message.author.name) + ', what did the table do to you?')

		if bot.gpio_enabled == "yes":
			GPIO.output(statPin,0)


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	global serv
	serv = discord.utils.find(lambda m: m.name == bot.server_name, client.servers)
	KT_role = discord.utils.find(lambda m: m.name == "KT", serv.roles)

#if not client.is_logged_in:
#	print('Logging in to Discord failed')
#	exit(1)

client.run(bot.get_bot_credential('token'))
try:
	GPIO.cleanup()
except:
	pass

