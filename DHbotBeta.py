import datetime
import json
import logging
import os
import requests

import dice
import discord
import gw2api

##################
# Global variables
##################

EVENT_TEXT_FILE = "events.txt"
HELP_TEXT_FILE = 'help.txt'

#Functions
def get_bot_credential(credential):
	x = open('BotCred.txt', 'r')
	bot_json = json.load(x)
	x.close()
	return bot_json[credential]

def check_role(message, role_test):
	mem = discord.utils.find(lambda m: m.id == message.author.id, message.channel.server.members)
	user_roles = []
	for x in mem.roles:
		user_roles.append(x.name)

	if role_test in user_roles:
		return True
	else:
		return False

def check_user_role(member, role_test):
	mem = discord.utils.find(lambda m: m.id == member.id, member.server.members)
	user_roles = []
	for x in mem.roles:
		user_roles.append(x.name)

	if role_test in user_roles:
		return True
	else:
		return False


def weekly_event(event_day, event_hour, event_minute):
	"""
	This function computes the timedelta for events that occur weekly.

	event_day is an integer between 0 and 6, where 0 is monday and 6 is sunday.
	event_hour is an integer between 0 and 23
	event_minute is an integer between 0 and 59

	Provide these times in UTC

	event_time is a datetime object. The day is initially set to be the same as the current day.
	This value is then altered based on a comparison with event_day, due to the lack of 
	support for days of the week.
	"""
	now = datetime.datetime.utcnow()
	event_time = datetime.datetime(now.year, now.month, now.day, hour=event_hour, minute=event_minute)

	if event_day > now.weekday():
		x = event_day - now.weekday()
		event_time = event_time + datetime.timedelta(days=x)
		return (event_time - now)
	elif event_day < now.weekday():
		x = abs(event_day - now.weekday())
		event_time = event_time + datetime.timedelta(days=(7-x))
		return (event_time - now)
	elif event_day == now.weekday():
		if event_time.hour > now.hour:
			return (event_time - now)
		elif event_time.hour < now.hour:
			event_time = event_time + datetime.timedelta(days=7)
			return (event_time - now)
		elif event_time.hour == now.hour:
			if event_time.minute > now.minute:
				return (event_time - now)
			elif event_time.minute == now.minute or event_time.minute < now.minute:
				event_time = event_time + datetime.timedelta(days=7)
				return (event_time - now)

def daily_event(event_hour, event_minute):
	now = datetime.datetime.utcnow()
	event_time = datetime.datetime(now.year, now.month, now.day, hour=event_hour, minute=event_minute)

	if event_time > now:
		return (event_time - now)
	elif event_time == now or event_time < now:
		event_time = event_time + datetime.timedelta(days=1)
		return (event_time - now)


# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

# Initialize client object, begin connection
client = discord.Client()
client.login(get_bot_credential('Username'), get_bot_credential('Password'))

if not client.is_logged_in:
	print('Logging in to Discord failed')
	exit(1)

# Event handler
@client.event
def on_member_join(newmember):
	admin_users = []
	for x in newmember.server.members:
		if check_user_role(x, 'BotManager') == True:
			admin_users += [x]
	notification_channel = discord.utils.find(lambda m: m.name == 'botbeta', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += ' '+str(x.mention())
	client.send_message(notification_channel, newmember.name + ' needs permissions. {}'.format(admin_mentions))
#	client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible. In the meantime, you are free to use the lobby text chat and Public voice channels. Please be sure to read the announcements as well. You may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.')

@client.event
def on_message(message):

	if message.content.startswith('!events'):
		text_file = open(EVENT_TEXT_FILE, 'r')
		client.send_message(message.channel, text_file.read())
		text_file.close()

	if message.content.startswith('!events_edit'):
		if check_role(message, 'BotManager') == True:
			text_file = open(EVENT_TEXT_FILE, 'w')
			new_event_text = message.content.partition(' ')[2]
			trim_event_text = new_event_text[0:1999]
			text_file.write(trim_event_text)
			text_file.close()
			client.delete_message(message)
			client.send_message(message.channel, str(message.author) +' has updated the event message.')
		else:
			client.send_message(message.channel, 'You do not have permission to edit the event message.')

	if message.content.startswith('!hello'):
		client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))

	if message.content.startswith('!help'):
		text_file = open(HELP_TEXT_FILE, 'r')
		client.send_message(message.channel, text_file.read())
		text_file.close()

	if message.content.startswith('!price'):
		item_name = message.content.partition(' ')[2]
		response1 = requests.get("http://www.gw2spidy.com/api/v0.9/json/item-search/"+item_name)
		item_results = json.loads(response1.text)
		testresults = item_results['results']
		for x in range(len(testresults)):
			if str(item_name).lower() == str(testresults[x]['name']).lower():
				itemid = testresults[x]['data_id']
		response2 = requests.get("https://api.guildwars2.com/v2/commerce/prices/"+str(itemid))
		listing = json.loads(response2.text)
		buy_price_raw = listing['buys']['unit_price']
		sell_price_raw = listing['sells']['unit_price']
		bsilver, bcopper = divmod(buy_price_raw, 100)
		bgold, bsilver = divmod(bsilver, 100)
		ssilver, scopper = divmod(sell_price_raw, 100)
		sgold, ssilver = divmod(ssilver, 100)
		client.send_message(message.channel, 'The current buy price of ' +item_name +' is ' +str(bgold).zfill(2) +'g ' +str(bsilver).zfill(2)+ 's ' +str(bcopper).zfill(2)+ 'c. \nThe current sell price is ' +str(sgold).zfill(2) +'g ' +str(ssilver).zfill(2)+ 's ' +str(scopper).zfill(2)+ 'c.')

	if message.content.startswith('!timetohot'):
		time_remaining = datetime.datetime(2015, 10, 23,2,1) - datetime.datetime.now()
		m, s = divmod(time_remaining.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'The time remaining to HoT launch is: ' +str(time_remaining.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')

	if message.content.startswith('!timetomissions'):
		mission_time_delta = weekly_event(6, 1, 10)
		m, s = divmod(mission_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until guild missions: ' +str(mission_time_delta.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.\n Meet in Queensdale!')

	if message.content.startswith('!timetoreset'):
		reset_time_delta = daily_event(0, 0)
		m, s = divmod(reset_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until reset: ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')

	if message.content.startswith('!timetowvwreset'):
		wvw_time_delta = weekly_event(5, 0, 0)
		m, s = divmod(wvw_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until WvW reset: ' + str(wvw_time_delta.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')

	if message.content.startswith('!lmgtfy'):
		search = message.content.partition(' ')[2].replace(' ','+')
		client.send_message(message.channel, 'http://lmgtfy.com/?q='+search)

	if message.content.startswith('!wiki'):
		search = message.content.partition(' ')[2].replace(' ', '_')
		client.send_message(message.channel, 'http://wiki.guildwars2.com/wiki/Special:Search/'+search)

	if message.content.startswith('!quit'):
		if check_role(message, 'BotManager') == True:
			client.logout()
		else:
			client.send_message(message.channel, 'You do not have permission to stop DHBot.')

	if message.content.startswith('!worldbosses'):
		pass

	if '(╯°□°）╯︵ ┻━┻' in message.content:
		client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ) \n\n' +str(message.author.name) + ', what did the table do to you?')

	if message.content.startswith('!roll'):
		droll = message.content.partition(' ')[2]
		client.send_message(message.channel, str(dice.roll(droll)))

#	if message.content.startswith('!fractal'):
#		fractal_level = message.content.partition(' ')[2]
#		text_file = open('fractal'+str(fractal_level)+'.txt', 'r')
#		client.send_message(message.channel, 'Would you like to do a 50 fractal? ' + str(text_file.read()))
#		text_file.close()

#	if message.content.startswith('!add_fractal'):
#		fractal_level = message.content.partition(' ')[2]
#		f = open('fractal.txt', 'r')
#		f_list = json.load(f)[str(fractal_level)]
#		f.close()
#		#if message.author not in f_list:
#		f_list.append(message.author)
#			with open('fractal'+fractal_level+'.txt', 'a') as g:
#				g.write(''.format(message.author.mention))
		#	client.send_message(message.channel, str(message.author.name) + ', you have been added to the fractal ' +str(fractal_level) + ' list.')
		#else:
		#	client.send_message(message.channel, str(message.author.name) + ', you are already on that list.')


#@client.event
#def on_message(message):
#	if message.content.startswith('!id'):
#		item_name = message.content.partition(' ')[2]
#		response = requests.get("http://www.gw2spidy.com/api/v0.9/json/item-search/"+item_name)
#		item_results = json.loads(response.text)
#		item_id = item_results['results'][0]['data_id']
#		client.send_message(message.channel, item_id)
		

@client.event
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run()