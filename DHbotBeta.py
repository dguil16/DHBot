import requests
import discord
import logging
import os
import json
import gw2api
import urllib.request
import urllib.error
import datetime

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

client = discord.Client()
client.login('zendevarbot@gmail.com', 'Flower4Jewel13')

if not client.is_logged_in:
	print('Logging in to Discord failed')
	exit(1)

@client.event
def on_message(message):
	if message.content.startswith('!hello'):
		client.send_message(message.channel, 'Hello {}!'.format(message.author.mention()))

	if message.content.startswith('!events'):
		file_location = os.path.normpath("C:/Users/Daniel/Google Drive/DH Stuff/events.txt")
		stuff = open(file_location, 'r')
		client.send_message(message.channel, stuff.read())
		stuff.close()

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
		client.send_message(message.channel, 'The current buy price of ' +found_name +' is ' +str(bgold).zfill(2) +'g ' +str(bsilver).zfill(2)+ 's ' +str

(bcopper).zfill(2)+ 'c. \nThe current sell price is ' +str(sgold).zfill(2) +'g ' +str(ssilver).zfill(2)+ 's ' +str(scopper).zfill(2)+ 'c.')

	if message.content.startswith('!timetohot'):
		time_remaining = datetime.datetime(2015, 10, 23,2,1) - datetime.datetime.now()
		m, s = divmod(time_remaining.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'The time remaining to HoT launch is: ' +str(time_remaining.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' 

+ str(s) + ' seconds.')

	if message.content.startswith('!test'):
		username = message.author
		servmem = server.member(username)
		#role = username.roles
		client.send_message(message.channel, str(servmem))

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
