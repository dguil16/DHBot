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

async def call(client, message, kind, info):
	last_update_raw = os.path.getmtime('fractal_users.txt')
	last_update = datetime.fromtimestamp(last_update_raw)
	update_time = datetime.now() - last_update
	try:
		with open("fractal_users.txt", 'r') as f:
			fractal_users = json.load(f)
	except:
		fractal_users = {}
	if update_time.total_seconds() > 300: #55 minutes = 600 seconds
		for Discord_ID in fractal_users:
			API_key = fractal_users[Discord_ID]["API Key"]
			response = requests.get("https://api.guildwars2.com/v2/account?access_token={}".format(API_key))
			if response != {"text": "invalid key"}:
				fractal_level = json.loads(response.text)["fractal_level"]
				fractal_users[Discord_ID]["fractal_level"] = fractal_level
			response = requests.get("https://api.guildwars2.com/v2/account/achievements?access_token={}".format(API_key))
			if response != {"text": "invalid key"}:
				all_achievs = json.loads(response.text)
				fractal_achievs = {}
				for y in all_achievs:
					if y["id"] in {2965, 2894, 2217, 2415}:
						fractal_achievs[y["id"]] = y
						fractal_users[Discord_ID]["Fractal Achievements"] = [fractal_achievs]
		with open("fractal_users.txt", 'w') as f:
			f.write(str(json.dumps(fractal_users)))

	if kind == 'level':
		frac_level = info
		candidates = []
		for x in fractal_users:
			if int(fractal_users[x]["fractal_level"]) >= int(frac_level) - 5:
				candidates = candidates + [str(x)]

	else:
		return False;
#Check achievs
		
	return candidates;


async def enroll(client, message, Discord_ID, API_key):
	try:
		response = requests.get("https://api.guildwars2.com/v2/tokeninfo?access_token={}".format(API_key))
		API_key_info = json.loads(response.text)
	except:
		await client.delete_message(message)
		await client.send_message(message.channel, "There seems to be an error with your API key. Please ensure it is correct and try again. The original message was deleted for security purposes.")
	if API_key_info == {"text": "invalid key"} or API_key_info == {"text": "endpoint requires authentication"}:
		await client.send_message(message.channel, "It looks like you did not enter a valid GW2 API key. Please try again.")
	elif set(API_key_info["permissions"]).intersection(set(["builds", "progression", "account", "characters"])) != {"builds", "progression", "account", "characters"}:
		await client.delete_message(message)
		await client.send_message(message.channel, "This API key does not have the proper permissions. Please ensure the key has the Account, Characters, Builds, and Progression permissions. The original message was deleted for security purposes.")
	else:
		try:
			with open("fractal_users.txt", 'r') as f:
				fractal_users = json.load(f)
		except:
			fractal_users = {}
		if Discord_ID in fractal_users:
			response_content = "The API key for " + message.author.name + " has been updated in the Fractal list."
		else:
			response_content = message.author.mention + " has enrolled in the Fractal list."
		if message.channel.is_private == False:
			await client.delete_message(message)
			response_content = response_content + " The original message has been deleted for security purposes."
		fractal_users[Discord_ID] = {"API Key": API_key}
		response = requests.get("https://api.guildwars2.com/v2/account?access_token={}".format(API_key))
		fractal_level = json.loads(response.text)["fractal_level"]
		fractal_users[Discord_ID]["fractal_level"] = fractal_level
		response = requests.get("https://api.guildwars2.com/v2/account/achievements?access_token={}".format(API_key))
		all_achievs = json.loads(response.text)
		fractal_achievs = {}
		for x in all_achievs:
			if x["id"] in {2965, 2894, 2217, 2415}:
				fractal_achievs[x["id"]] = x 
		fractal_users[Discord_ID]["Fractal Achievements"] = [fractal_achievs]
			
		with open("fractal_users.txt", 'w') as f:
			f.write(str(json.dumps(fractal_users)))
		await client.send_message(message.channel, response_content)


async def unenroll(client, message, Discord_ID):
	try: 
		with open("fractal_users.txt", 'r') as f:
			fractal_users = json.load(f)
	except:
		fractal_users = {}
	try:
		del fractal_users[Discord_ID]
		with open("fractal_users.txt", 'w') as f:
			f.write(str(json.dumps(fractal_users)))
		await client.send_message(message.channel, message.author.mention + " was removed from the Fractal list.")
	except:
		await client.send_message(message.channel, "There was an error with your request. Likely, you are not currently a member of the Fractal list.")
