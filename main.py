
import logging

import discord

import chatbot

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

# Create a new instance of a chatbot object
bot = chatbot.chatbot('BotCred.txt', 'events.txt', 'help.txt')

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
	notification_channel = discord.utils.find(lambda m: m.name == 'botbeta', newmember.server.channels)
	admin_mentions = ''
	for x in admin_users:
		admin_mentions += ' '+str(x.mention())
	client.send_message(notification_channel, newmember.name + ' needs permissions. {}'.format(admin_mentions))
#	client.send_message(newmember, 'Welcome to our Discord server. My name is ' +client.user.name +', the chat bot for this server. I have sent a message to the server Admins to let them know you have joined. They will give you appropriate permissions as soon as possible. In the meantime, you are free to use the lobby text chat and Public voice channels. Please be sure to read the announcements as well. You may also utilize some of my functions by responding to this message or, once you have permissions, by posting in the botbeta channel. To find a list of my functions, you may type !help.')

@client.event
def on_message(message):
	if bot.check_role(message, 'BotBan') == False:
		if message.content.startswith('!events'):
			bot.file_read(client, message, 'events')

		if message.content.startswith('!events_edit'):
			bot.file_edit(client, message, 'events')

		if message.content.startswith('!fractal'):
			bot.fractal(client, message)

		if message.content.startswith('!fractal_add'):
			bot.fractal_add(client, message)

		if message.content.startswith('!hello'):
			bot.greet(client, message)

		if message.content.startswith('!help'):
			bot.file_read(client, message, 'help')

		if message.content.startswith('!help_edit'):
			bot.file_edit(client, message, 'help')

		if message.content.startswith('!price'):
			bot.price(client, message)

		if message.content.startswith('!timetohot'):
			bot.time_to_hot(client, message)

		if message.content.startswith('!timetomissions'):
			bot.time_to_missions(client, message)

		if message.content.startswith('!timetoreset'):
			bot.time_to_reset(client, message)

		if message.content.startswith('!timetowvwreset'):
			bot.time_to_wvw_reset(client, message)

		if message.content.startswith('!lmgtfy'):
			bot.lmgtfy(client, message)

		if message.content.startswith('!wiki'):
			bot.wiki(client, message)

		if message.content.startswith('!quit'):
			bot.stop_bot(client, message)

		if message.content.startswith('!worldbosses'):
			pass

		if '(╯°□°）╯︵ ┻━┻' in message.content:
			client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ) \n\n' +str(message.author.name) + ', what did the table do to you?')

		if message.content.startswith('!roll'):
			bot.roll_dice(client, message)


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