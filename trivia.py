import discord
import json

trivia_answer = ''

class Trivia(object):

	def __init__(self):
		pass

	def trivia_fncs(self, client, message):
		f = open('trivia.txt', 'r')
		all_trivia = json.load(f)
		f.close()

		if message.content.startswith('!trivia-create'):
			set_name = message.content.partition(' ')[2]
			all_trivia["Names"].append(set_name)
			all_trivia[set_name] = {"Questions": {}, "Answers": {}, "Current Question": "0", "Winners":{}}

		if message.content.startswith('!trivia-delete'):
			set_name = message.content.partition(' ')[2]
			all_trivia["Names"].remove(set_name)
			del all_trivia[set_name]
			if all_trivia["Current Set"] == set_name:
				all_trivia["Current Set"] = ""

		if message.content.startswith('!trivia-editQA'):
			trivia_data = message.content.partition(' ')[2]
			set_name = trivia_data.split('; ')[0]
			question_number = trivia_data.split('; ')[1]
			question = trivia_data.split('; ')[2]
			answer = trivia_data.split('; ')[3]
			all_trivia[set_name]["Questions"][question_number] = question
			all_trivia[set_name]["Answers"][question_number] = answer

		if message.content.startswith('!trivia-QA'):
			trivia_data = message.content.partition(' ')[2]
			set_name = trivia_data.split('; ')[0]
			question = trivia_data.split('; ')[1]
			answer = trivia_data.split('; ')[2]
			total_questions = len(all_trivia[set_name]["Questions"])
			all_trivia[set_name]["Questions"][int(total_questions)] = question
			all_trivia[set_name]["Answers"][int(total_questions)] = answer

		if message.content.startswith('!trivia-start'):
			set_name = message.content.partition(' ')[2]
			all_trivia["Current Set"] = set_name
			current_number = all_trivia[set_name]["Current Question"]
			client.send_message(message.channel, 'Trivia is starting! It is time for the first question! \n\n' + all_trivia[set_name]["Questions"][current_number])
			global trivia_answer
			trivia_answer = str(all_trivia[set_name]["Answers"][current_number])

		if message.content.startswith('!trivia-end'):
			all_trivia["Current Set"] = ""
			client.send_message(message.channel, 'Trivia has ended.')
			global trivia_answer
			trivia_answer = ''

		if message.content.startswith('!trivia-next'):
			current_set = all_trivia["Current Set"]
			current_number = all_trivia[current_set]["Current Question"]
			client.send_message(message.channel, all_trivia[current_set]["Questions"][current_number])
			global trivia_answer
			trivia_answer = all_trivia[current_set]["Answers"][current_number]

		if message.content.startswith('!trivia-goto'):
			question_number = message.content.partition(' ')[2]
			current_set = all_trivia["Current Set"]
			all_trivia[current_set]["Current Question"] = str(question_number)
			global trivia_answer
			trivia_answer = all_trivia[current_set]["Answers"][question_number]

		g = open('trivia.txt', 'w')
		g.write(str(json.dumps(all_trivia)))
		g.close()

	def correct_answer(self, client, message):
		client.send_message(message.channel, message.author.name + ' has answered the question correctly!')
		f = open('trivia.txt', 'r')
		all_trivia = json.load(f)
		f.close()
		current_set = all_trivia["Current Set"]
		current_number = all_trivia[current_set]["Current Question"]
		all_trivia[current_set]["Current Question"] = str(int(current_number)+1)
		global trivia_answer
		trivia_answer = ''
		g = open('trivia.txt', 'w')
		g.write(str(json.dumps(all_trivia)))
		g.close()