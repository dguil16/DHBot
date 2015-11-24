import discord
import json

class Poll(object):
	def __init__(self):
		pass

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

	def poll_fnc(self, client, message, query):
		try:
			poll_query = message.content.partition(' ')[2]
			poll_name = poll_query.split('; ')[0]
			f = open('polls.txt', 'r')
			all_polls = json.load(f)
			f.close()
			
			if query == 'create anon':
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
						poll_content = {"Description": poll_desc, "Options": poll_opt, "Totals":vote_list, "Voters":[], "Author": message.author.name, "Status": "Open", "Anon": "Yes", "Type": "Single"}
						all_polls[poll_name] = poll_content
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, 'The poll \"' + poll_name +'\" has been created.')
				else:
					client.send_message(message.channel, 'You do not have permission to create polls at this time.')

			if query == 'create multi':
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
						poll_content = {"Description": poll_desc, "Options": poll_opt, "Totals":vote_list, "Voters":[], "Votes": {}, "Author": message.author.name, "Status": "Open", "Anon": "No", "Type": "Multi"}
						all_polls[poll_name] = poll_content
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, 'The poll \"' + poll_name +'\" has been created.')
				else:
					client.send_message(message.channel, 'You do not have permission to create polls at this time.')

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
						poll_content = {"Description": poll_desc, "Options": poll_opt, "Totals":vote_list, "Votes": {}, "Voters":[], "Author": message.author.name, "Status": "Open", "Anon": "No", "Type": "Single"}
						all_polls[poll_name] = poll_content
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, 'The poll \"' + poll_name +'\" has been created.')
				else:
					client.send_message(message.channel, 'You do not have permission to create polls at this time.')

			if query == 'delete':
				if self.check_role(message, 'Admin') == True or message.author.name == all_polls[poll_name]["Author"]:
					all_polls["Names"].remove(poll_name)
					del all_polls[poll_name]
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, 'The poll \"' + poll_name + '\" has been deleted.')
				else:
					client.send_message(message.channel, 'You do not have permission to delete this poll.')

			if query == 'vote':
				if all_polls[poll_name]["Status"] == "Closed":
					client.send_message(message.channel, "That poll is currently closed.")
				
				elif message.author.name in all_polls[poll_name]["Voters"] and all_polls[poll_name]["Type"] == "Single":
					client.send_message(message.channel, 'You have already voted in this poll.')
				
				elif all_polls[poll_name]["Anon"] == "Yes":
					all_polls[poll_name]["Voters"].append(message.author.name)
					vote = poll_query.partition('; ')[2]
					all_polls[poll_name]["Totals"][vote] += 1
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, message.author.name + '\'s vote for ' + vote + ' has been recorded.')
				
				elif all_polls[poll_name]["Anon"] == "No" and all_polls[poll_name]["Type"] == "Single":
					vote = poll_query.partition('; ')[2]
					all_polls[poll_name]["Voters"].append(message.author.name)
					all_polls[poll_name]["Votes"][message.author.name] = [vote]
					all_polls[poll_name]["Totals"][vote] += 1
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, message.author.name + '\'s vote for ' + vote + ' has been recorded.')
				
				elif all_polls[poll_name]["Type"] == "Multi":
					vote = poll_query.partition('; ')[2]
					if message.author.name not in all_polls[poll_name]["Voters"]:
						all_polls[poll_name]["Voters"].append(message.author.name)
						all_polls[poll_name]["Votes"][message.author.name] = []
					if vote in all_polls[poll_name]["Votes"][message.author.name]:
						client.send_message(message.channel, 'You have already voted for ' + vote + '.')
					else:
						all_polls[poll_name]["Votes"][message.author.name] += [vote]
						all_polls[poll_name]["Totals"][vote] += 1
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, message.author.name + '\'s vote for ' + vote + ' has been recorded.')

			if query == 'vote remove':
				vote = poll_query.partition('; ')[2]
				if all_polls[poll_name]["Anon"] == "Yes":
					client.send_message(message.channel, "The votes for this poll are anonymous, so changes cannot be made.")
				elif vote not in all_polls[poll_name]["Votes"][message.author.name]:
					client.send_message(message.channel, "You have not voted for " + vote +".")
				elif all_polls[poll_name]["Anon"] == "No":
					if all_polls[poll_name]["Type"] == "Single":
						all_polls[poll_name]["Voters"].remove(message.author.name)
					all_polls[poll_name]["Votes"][message.author.name].remove(vote)
					all_polls[poll_name]["Totals"][vote] += -1
					f = open('polls.txt', 'w')
					f.write(str(json.dumps(all_polls)))
					f.close()
					client.send_message(message.channel, "Your vote for " + vote + " has been removed.")


			if query == 'admin':
				if self.check_role(message, 'Admin') == True or message.author.name == all_polls[poll_name]["Author"]:
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
				client.send_message(message.channel, poll_name + ':\n\n' + all_polls[poll_name]["Description"] + '\n\nThe options for this poll are: ' + all_polls[poll_name]["Options"] +'\n\nType:' + all_polls[poll_name]["Type"] +'\n\nStatus: ' + all_polls[poll_name]["Status"] + '\n\nAuthor: ' + all_polls[poll_name]["Author"])

			if query == 'results':
				client.send_message(message.channel, 'The current vote totals are as follows:\n\n' + str(all_polls[poll_name]["Totals"]))

			if query == 'open':
				if self.check_role(message, 'Admin') == True or message.author.name == all_polls[poll_name]["Author"]:
					if all_polls[poll_name]['Status'] == 'Open':
						client.send_message(message.channel, 'That poll is already open.')
					else:
						all_polls[poll_name]["Status"] = "Open"
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, message.author.name + ' has opened the poll ' + poll_name + '.')
				else:
					client.send_message(message.channel, 'You do not have permission to modify this poll.')

			if query == 'close':
				if self.check_role(message, 'Admin') == True or message.author.name == all_polls[poll_name]["Author"]:
					if all_polls[poll_name]['Status'] == 'Closed':
						client.send_message(message.channel, 'That poll is already closed.')
					else:
						all_polls[poll_name]["Status"] = "Closed"
						f = open('polls.txt', 'w')
						f.write(str(json.dumps(all_polls)))
						f.close()
						client.send_message(message.channel, message.author.name + ' has closed the poll ' + poll_name + '.')
				else:
					client.send_message(message.channel, 'You do not have permission to modify this poll.')

		except:
			client.send_message(message.channel, 'There was an error in your request. Please try again.')

	def survey_fnc(self, client, message, query):
		try:
			survey_query = message.content.partition(' ')[2]
			survey_name = survey_query.split('; ')[0]
			f = open('surveys.txt', 'r')
			all_surveys = json.load(f)
			f.close()
			
			if query == 'create':
				if self.check_role(message, 'Leadership') == True:
					survey_desc = survey_query.partition('; ')[2]
					if survey_name in all_surveys["Names"]:
						client.send_message(message.channel, 'There is already a survey with that name.')
					else:
						all_surveys["Names"].append(survey_name)
						survey_content = {"Description": survey_desc, "Entries": {}, "Voters":[], "Author": message.author.name, "Status": "Open"}
						all_surveys[survey_name] = survey_content
						f = open('surveys.txt', 'w')
						f.write(str(json.dumps(all_surveys)))
						f.close()
						client.send_message(message.channel, 'The survey \"' + survey_name +'\" has been created.')
				else:
					client.send_message(message.channel, 'You do not have permission to create surveys at this time.')

			if query == 'delete':
				if self.check_role(message, 'Admin') == True or message.author.name == all_surveys[survey_name]["Author"]:
					all_surveys["Names"].remove(survey_name)
					del all_surveys[survey_name]
					f = open('surveys.txt', 'w')
					f.write(str(json.dumps(all_surveys)))
					f.close()
					client.send_message(message.channel, 'The survey \"' + survey_name + '\" has been deleted.')
				else:
					client.send_message(message.channel, 'You do not have permission to delete this survey.')

			if query == 'submit':
				if all_surveys[survey_name]["Status"] == "Closed":
					client.send_message(message.channel, "That survey is currently closed.")
				elif message.author.name in all_surveys[survey_name]["Voters"]:
					client.send_message(message.channel, 'You have already submitted an answer to this survey.')
				else:
					all_surveys[survey_name]["Voters"].append(message.author.name)
					vote = survey_query.partition('; ')[2]
					all_surveys[survey_name]["Entries"][message.author.name] = vote
					f = open('surveys.txt', 'w')
					f.write(str(json.dumps(all_surveys)))
					f.close()
					client.send_message(message.channel, 'Your survey submission has been recorded.')

			if query == 'change':
				if all_surveys[survey_name]["Status"] == "Closed":
					client.send_message(message.channel, "That survey is currently closed.")
				elif message.author.name not in all_surveys[survey_name]["Voters"]:
					client.send_message(message.channel, 'You have not yet submitted an answer to this survey. Please use !survey-submit instead.')
				else:
					vote = survey_query.partition('; ')[2]
					all_surveys[survey_name]["Entries"][message.author.name] = vote
					f = open('surveys.txt', 'w')
					f.write(str(json.dumps(all_surveys)))
					f.close()
					client.send_message(message.channel, 'Your survey submission has been recorded.')

			if query == 'list':
				client.send_message(message.channel, 'The current surveys are: ' +str(all_surveys["Names"]))

			if query == 'info':
				client.send_message(message.channel, survey_name + '\n\n' + all_surveys[survey_name]["Description"] + '\n\nStatus: ' + all_surveys[survey_name]["Status"] + '\n\nAuthor: ' + all_surveys[survey_name]["Author"])

			if query == 'results':
				if self.check_role(message, 'Admin') == True or message.author.name == all_surveys[survey_name]["Author"]:
					for x in sorted(all_surveys[survey_name]["Voters"]):
						client.send_message(message.author, x + ' submitted: \n' + all_surveys[survey_name]["Entries"][x] +'\n')
				else: client.send_message(message.channel, 'You do not have permission to view the survey results.')

			if query == 'open':
				if self.check_role(message, 'Admin') == True or message.author.name == all_surveys[survey_name]["Author"]:
					if all_surveys[survey_name]['Status'] == 'Open':
						client.send_message(message.channel, 'That survey is already open.')
					else:
						all_surveys[survey_name]["Status"] = "Open"
						f = open('surveys.txt', 'w')
						f.write(str(json.dumps(all_surveys)))
						f.close()
						client.send_message(message.channel, message.author.name + ' has opened the survey ' + survey_name + '.')
				else:
					client.send_message(message.channel, 'You do not have permission to modify this survey.')

			if query == 'close':
				if self.check_role(message, 'Admin') == True or message.author.name == all_surveys[survey_name]["Author"]:
					if all_surveys[survey_name]['Status'] == 'Closed':
						client.send_message(message.channel, 'That survey is already closed.')
					else:
						all_surveys[survey_name]["Status"] = "Closed"
						f = open('surveys.txt', 'w')
						f.write(str(json.dumps(all_surveys)))
						f.close()
						client.send_message(message.channel, message.author.name + ' has closed the survey ' + survey_name + '.')
				else:
					client.send_message(message.channel, 'You do not have permission to modify this survey.')
		except:
			client.send_message(message.channel, 'There was an error in your request. Please try again.')