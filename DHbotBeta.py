import datetime
import json
import logging
import os
import requests

import discord
import gw2api

###################
# Global variables#
###################

EVENT_TEXT_FILE = os.path.normpath("C:/Users/Daniel/Google Drive/DH Stuff/events.txt")

#Functions
def get_bot_credential(credential):
	x = open('BotCred.txt', 'r')
	bot_json = json.load(x)
	x.close()
	return bot_json[credential]

def check_role(role_test):
	mem = discord.utils.find(lambda m: m.id == message.author.id, message.channel.server.members)
	user_roles = []
	for x in mem.roles:
		user_roles.append(x.name)

	if role_test in user_roles:
		return True
	else:
		return False

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
def on_message(message):

	if message.content.startswith('!edit_events'):
		if check_role('Tester') == True:
			text_file = open(EVENT_TEXT_FILE, 'w')
			new_event_text = message.content.partition(' ')[2]
			trim_event_text = new_event_text[0:200]
			text_file.write(trim_event_text)
			text_file.close()

			client.send_message(message.channel, 'Your new message has been written.')
		else:
			client.send_message(message.channel, 'You do not have permission to edit the event message.')


	if message.content.startswith('!events'):
		text_file = open(EVENT_TEXT_FILE, 'r')
		client.send_message(message.channel, text_file.read())
		text_file.close()


	if message.content.startswith('!hello'):
		client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))


	if message.content.startswith('!help'):
		pass


	if message.content.startswith('!price'):
		item_name = message.content.partition(' ')[2]
		response1 = requests.get("http://www.gw2spidy.com/api/v0.9/json/item-search/"+item_name)
		item_results = json.loads(response1.text)
		found_name = item_results['results'][0]['name']
		item_id = item_results['results'][0]['data_id']
		response2 = requests.get("https://api.guildwars2.com/v2/commerce/prices/"+str(item_id))
		listing = json.loads(response2.text)
		buy_price_raw = listing['buys']['unit_price']
		sell_price_raw = listing['sells']['unit_price']
		bsilver, bcopper = divmod(buy_price_raw, 100)
		bgold, bsilver = divmod(bsilver, 100)
		ssilver, scopper = divmod(sell_price_raw, 100)
		sgold, ssilver = divmod(ssilver, 100)
		client.send_message(message.channel, 'The current buy price of ' +found_name +' is ' +str(bgold).zfill(2) +'g ' +str(bsilver).zfill(2)+ 's ' +str(bcopper).zfill(2)+ 'c. \nThe current sell price is ' +str(sgold).zfill(2) +'g ' +str(ssilver).zfill(2)+ 's ' +str(scopper).zfill(2)+ 'c.')


	if message.content.startswith('!timetohot'):
		time_remaining = datetime.datetime(2015, 10, 23,2,1) - datetime.datetime.now()
		m, s = divmod(time_remaining.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'The time remaining to HoT launch is: ' +str(time_remaining.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')


	if message.content.startswith('!test'):
		if check_role('Tester') == True:
			client.send_message(message.channel, 'You are a Tester')
		else:
			client.send_message(message.channel, 'You are not a Tester.')


	if message.content.startswith('!quit'):
		if check_role('Tester') == True:
			client.logout()
		else:
			client.send_message(message.channel, 'You do not have permission to stop DHBot.')

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