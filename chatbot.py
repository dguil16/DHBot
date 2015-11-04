import datetime
from datetime import datetime
import json
import requests

import dice
import discord

class Chatbot(object):
	"""docstring for chatbot"""

	def __init__(self, credential_location, event_text_file, help_text_file, fractal_text_file, mission_text_file):
		self.credential_location = credential_location
		self.event_text_file = event_text_file
		self.help_text_file = help_text_file
		self.fractal_text_file = fractal_text_file
		self.mission_text_file = mission_text_file

	def _weekly_event(self, event_day, event_hour, event_minute):
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
	
	def _daily_event(self, event_hour, event_minute):
		""" Like weekly_event, but for an event that repeats daily """
		now = datetime.datetime.utcnow()
		event_time = datetime.datetime(now.year, now.month, now.day, hour=event_hour, minute=event_minute)

		if event_time > now:
			return (event_time - now)
		elif event_time == now or event_time < now:
			event_time = event_time + datetime.timedelta(days=1)
			return (event_time - now)

	def check_role(self, message_or_member, role_test):
		if isinstance(message_or_member, discord.message.Message) == True:
			msg = message_or_member
			mem = discord.utils.find(lambda m: m.id == msg.author.id, msg.channel.server.members)
		elif isinstance(message_or_member, (discord.user.User)) == True:
			member = message_or_member
			mem = discord.utils.find(lambda m: m.id == member.id, member.server.members)

		user_roles = []
		for x in mem.roles:
			user_roles.append(x.name)

		if role_test in user_roles:
			return True
		else:
			return False

	def file_interface(self, client, message, file_name, query):
		if file_name == 'events':
			location = self.event_text_file
		elif file_name == 'help':
			location = self.help_text_file

		if query == 'read':
			text_file = open(location, 'r')
			client.send_message(message.channel, text_file.read())
			text_file.close()
		elif query == 'write':
			if self.check_role(message, 'BotManager') == True:
				text_file = open(location, 'w')
				new_text = message.content.partition(' ')[2]
				text_file.write(new_text)
				text_file.close()
				client.delete_message(message)
				client.send_message(message.channel, str(message.author) +' has updated the ' + str(file_name) + ' message.')
			else:
				client.send_message(message.channel, 'You do not have permission to edit the ' + str(file_name) + ' message.')

	def clear(self, client, message):
		if self.check_role(message, 'Admin') == True:
			split_message = message.content.split(' ', 2)
			chan_name = split_message[1]
			chan = discord.utils.find(lambda m: m.name == chan_name, message.channel.server.channels)
			message_list = []
			for x in client.logs_from(chan):
				message_list += [x]
			list_to_delete = message_list[0:int(split_message[2])]
			for x in list_to_delete:
				client.delete_message(x)
		else:
			client.send_message(message.channel, 'I can\'t let you do that, ' + message.author.name +'.')

	def fractal(self, client, message, query):
		fractal_level = message.content.partition(' ')[2]
		f = open(self.fractal_text_file, 'r')
		fractal_list = json.load(f)
		f.close()

		if query == 'send':
			fractal_members = []
			fractal_mentions = ''
			for x in fractal_list[fractal_level]:
				user = discord.utils.find(lambda m: m.name == x, message.channel.server.members)
				fractal_members += [user]
			for x in fractal_members:
				fractal_mentions += str(x.mention()) + ' '
			client.send_message(message.channel, 'Would you like to do a ' + str(fractal_level) + ' fractal? ' + str(fractal_mentions))

		elif query == 'add':
			if message.author.name not in fractal_list[fractal_level]:
				fractal_list[fractal_level].append(message.author.name)
				with open(self.fractal_text_file, 'w') as g:
					g.write(str(json.dumps(fractal_list)))
				client.delete_message(message)
				client.send_message(message.channel, str(message.author.name) + ', you have been added to the fractal ' +str(fractal_level) + ' list.')
			else:
				client.send_message(message.channel, str(message.author.name) + ', you are already on that list.')

		elif query == 'remove':
			if message.author.name in fractal_list[fractal_level]:
				fractal_list[fractal_level].remove(message.author.name)
				with open(self.fractal_text_file, 'w') as g:
					g.write(str(json.dumps(fractal_list)))
				client.delete_message(message)
				client.send_message(message.channel, str(message.author.name) + ', you have been removed from the fractal level ' +str(fractal_level) + ' list.')
			else:
				client.send_message(message.channel, str(message.author.name) + ', you are not currently on the fractal level ' +str(fractal_level) + ' list.')

	def get_bot_credential(self, credential):
		""" Extracts the paramater credential from a formatted text file """
		x = open(self.credential_location, 'r')
		bot_json = json.load(x)
		x.close()
		return bot_json[credential]

	def greet(self, client, message):
		client.send_message(message.channel, 'Howdy {}!'.format(message.author.mention()))

	def lmgtfy(self, client, message):
		search = message.content.partition(' ')[2].replace(' ','+')
		client.send_message(message.channel, 'http://lmgtfy.com/?q='+search)

	def mission(self, client, message):
		mission = message.content.partition(' ' )[2]
		with open('mission.txt', 'r') as f:
			mission_data = json.load(f)
		client.send_message(message.channel, mission_data[mission])	

	def price(self, client, message):
		try:
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
		except:
			client.send_message(message.channel, 'There was an error processing your request.')

	def purge(self, client, message):
		if self.check_role(message, 'Admin') == True:
			split_message = message.content.split(' ', 2)
			user_name = split_message[1]
			user = discord.utils.find(lambda m: m.name == user_name, message.channel.server.members)
			message_list = []
			for x in client.logs_from(message.channel):
				if x.author.name == user.name:
					message_list += [x]
			list_to_delete = message_list[0:int(split_message[2])]
			for x in list_to_delete:
				client.delete_message(x)
		else:
			client.send_message(message.channel, 'I can\'t let you do that, ' +message.author.name)

	def roll_dice(self, client, message):
		droll = message.content.partition(' ')[2]
		clean = droll.split('d')
		if 0 < int(clean[0]) < 51 and 0 < int(clean[1]) < 1001:
			client.send_message(message.channel, str(dice.roll(droll)))
		else:
			client.send_message(message.channel, 'Not an appropriate amount or size of dice.')

	def stop_bot(self, client, message):
		if self.check_role(message, 'BotManager') == True:
			client.logout()
		else:
			client.send_message(message.channel, 'You do not have permission to stop DHBot.')

	def time_to_missions(self, client, message):
		mission_time_delta = self._weekly_event(6, 1, 10)
		m, s = divmod(mission_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until guild missions: ' +str(mission_time_delta.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.\n Meet in Queensdale!')

	def time_to_reset(self, client, message):
		reset_time_delta = self._daily_event(0, 0)
		m, s = divmod(reset_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until reset: ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')

	def time_to_wvw_reset(self, client, message):
		wvw_time_delta = self._weekly_event(5, 0, 0)
		m, s = divmod(wvw_time_delta.seconds, 60)
		h, m = divmod(m, 60)
		client.send_message(message.channel, 'Time remaining until WvW reset: ' + str(wvw_time_delta.days) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes ' + str(s) + ' seconds.')

	def wiki(self, client, message):
		search = message.content.partition(' ')[2].replace(' ', '_')
		client.send_message(message.channel, 'http://wiki.guildwars2.com/wiki/Special:Search/'+search)

	def poll(self, client, message, query):
		try:
			poll_query = message.content.partition(' ')[2]
			poll_name = poll_query.split('; ')[0]
			f = open('polls.txt', 'r')
			all_polls = json.load(f)
			f.close()
			
			if query == 'create':
				if self.check_role(message, 'Leadership') == True:
					poll_desc = poll_query.split('; ')[1]
					poll_opt = poll_query.split('; ')[2]
					option_list = poll_opt.split(', ')
					if poll_name in all_polls["Names"]:
						client.send_message(message.channel, 'There is already a poll with that name.')
					else:
						all_polls["Names"].append(poll_name)
						vote_list = {}
						for x in option_list:
							vote_list[x] = 0
						poll_content = {"Description": poll_desc, "Options": poll_opt, "Votes":vote_list, "Voters":[]}
						all_polls[poll_name] = poll_content
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, 'The poll \"' + poll_name +'\" has been created.')
				else:
					client.send_message(message.channel, 'You do not haver permission to create polls at this time.')

			if query == 'delete':
				if self.check_role(message, 'Leadership') == True:
					all_polls["Names"].remove(poll_name)
					del all_polls[poll_name]
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, 'The poll \"' + poll_name + '\" has been deleted.')
				else:
					client.send_message(message.channel, 'You do not haver permission to delete this poll.')

			if query == 'vote':
				if message.author.name in all_polls[poll_name]["Voters"]:
					client.send_message(message.channel, 'You have already voted in this poll.')
				else:
					all_polls[poll_name]["Voters"].append(message.author.name)
					vote = poll_query.split('; ')[1]
					all_polls[poll_name]["Votes"][vote] += 1
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, message.author.name + '\'s vote for ' + vote + ' has been recorded.')

			if query == 'admin':
				if self.check_role(message, 'Admin') == True:
					vote = poll_query.split('; ')[1]
					adjustment = int(poll_query.split('; ')[2])
					all_polls[poll_name]["Votes"][vote] += adjustment
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, message.author.name + ' has adjusted the vote for ' + vote + ' by ' + str(adjustment) + '.')
				else:
					client.send_message(message.channel, 'You do not have permission to use that function.')

			if query == 'list':
				client.send_message(message.channel, 'The current polls are: ' +str(all_polls["Names"]))

			if query == 'info':
				client.send_message(message.channel, 'The description of  ' + poll_name + ' is:\n\n' + all_polls[poll_name]["Description"] + '\n\nThe options for this poll are: \n\n' + all_polls[poll_name]["Options"])

			if query == 'results':
				client.send_message(message.channel, 'The current vote totals are as follows:\n\n' + str(all_polls[poll_name]["Votes"]))
		except:
			client.send_message(message.channel, 'There was an error in your request. Please try again.')