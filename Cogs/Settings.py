import asyncio
import discord
from   discord.ext import commands
import json
import os
from   Cogs import DisplayName


# This is the settings module - it allows the other modules to work with
# a global settings variable and to make changes

class Settings:
	"""The Doorway To The Server Settings"""
	# Let's initialize with a file location
	def __init__(self, bot, file : str = None):
		if file == None:
			# We weren't given a file, default to ./Settings.json
			file = "Settings.json"
		
		self.file = file
		self.bot = bot
		self.serverDict = {}

		self.defaultServer = { 						# Negates Name and ID - those are added dynamically to each new server
				"DefaultRole" 			: "", 		# Auto-assigned role position
				"DefaultXP"				: 0,		# Default xp given to each new member on join
				"DefaultXPReserve"		: 10,		# Default xp reserve given to new members on join
				"AdminLock" 			: "No", 	# Does the bot *only* answer to admins?
				"RequiredXPRole"		: "",		# ID or blank for Everyone
				"RequiredLinkRole" 		: "", 		# ID or blank for Admin-Only
				"RequiredHackRole" 		: "", 		# ID or blank for Admin-Only
				"RequiredKillRole" 		: "", 		# ID or blank for Admin-Only
				"RequiredStopRole"      : "",       # ID or blank for Admin-Only
				"MadLibsChannel"        : "",       # ID or blank for any channel
				"LastAnswer" 			: "",		# URL to last $question post
				"HourlyXP" 				: 3,		# How much xp reserve per hour
				"RequireOnline" 		: "Yes",	# Must be online for xp?
				"AdminUnlimited" 		: "Yes",	# Do admins have unlimited xp to give?
				"XPPromote" 			: "Yes",	# Can xp raise your rank?
				"XPDemote" 				: "No",		# Can xp lower your rank?
				"Killed" 				: "No",		# Is the bot dead?
				"KilledBy" 				: "",		# Who killed the bot?
				"LastPicture" 			: 0,		# UTC Timestamp of last picture uploaded
				"PictureThreshold" 		: 10,		# Number of seconds to wait before allowing pictures
				"Rules" 				: "Be nice to each other.",
				"PromotionArray" 		: [],		# An array of roles for promotions
				"Hunger" 				: 0,		# The bot's hunger % 0-100 (can also go negative)
				"HungerLock" 			: "No",		# Will the bot stop answering at 100% hunger?
				"Volume"				: "",		# Float volume for music player
				"DefaultVolume"			: 0.6,	# Default volume for music player
				"IgnoredUsers"			: [],		# List of users that are ignored by the bot
				"Hacks" 				: [],		# List of hack tips
				"Links" 				: [],		# List of links
				"Members" 				: [],		# List of members
				"AdminArray"	 		: [],		# List of admin roles
				"ChannelMOTD" 			: []}		# List of channel messages of the day
		
		# Let's load our settings file
		if os.path.exists(file):
			self.serverDict = json.load(open(file))
		else:
			# File doesn't exist - create a placeholder
			self.serverDict = {}
		
		# Removed for now as it may not be necessary,
		# Servers should auto-add whenever a user/server value
		# is requested or changed
		'''# Now we go through all the servers the bot is in and
		# make sure they're initialized
		for server in bot.servers:
			# Iterate through the servers and add them
			checkServer(server, globals.serverList)
			for user in server.members:
				checkUser(user, server, globals.serverList)'''

	def message(self, message):
		# Check the message and see if we should allow it - always yes.
		# This module doesn't need to cancel messages.
		return { 'Ignore' : False, 'Delete' : False}

	def getServerDict(self):
		# Returns the server dictionary
		return self.serverDict

	# Let's make sure the server is in our list
	def checkServer(self, server):
		# Assumes server = discord.Server and serverList is a dict
		if not "Servers" in self.serverDict:
			# Let's add an empty placeholder
			self.serverDict["Servers"] = []
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server
				found = True
				# Verify all the default keys have values
				for key in self.defaultServer:
					if not key in x:
						print("Adding: {}".format(key))
						x[key] = self.defaultServer[key]

		if not found:
			# We didn't locate our server
			# print("Server not located, adding...")
			# Set name and id - then compare to default server
			newServer = { "Name" : server.name, "ID" : server.id }
			for key in self.defaultServer:
				newServer[key] = self.defaultServer[key]
			
			self.serverDict["Servers"].append(newServer)
			self.flushSettings()

	# Let's make sure the user is in the specified server
	def removeServer(self, server):
		# Check for our server name
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				found = True
				# We found our server - remove
				self.serverDict["Servers"].remove(x)
		if found:
			self.flushSettings()

	def removeServerID(self, id):
		# Check for our server ID
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == id:
				found = True
				# We found our server - remove
				self.serverDict["Servers"].remove(x)
		if found:
			self.flushSettings()


	def removeChannel(self, channel):
		motdArray = self.settings.getServerStat(channel.server, "ChannelMOTD")
		for a in motdArray:
			# Get the channel that corresponds to the id
			if a['ID'] == channel.id:
				# We found it - throw an error message and return
				motdArray.remove(a)
				self.setServerStat(server, "ChannelMOTD", motdArray)


	def removeChannelID(self, id, server):
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				for y in x["ChannelMOTD"]:
					if y["ID"] == id:
						found = True
						x["ChannelMOTD"].remove(y)
	
	
	# Let's make sure the user is in the specified server
	def checkUser(self, user, server):
		# Make sure our server exists in the list
		self.checkServer(server)
		# Check for our username
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == user.id:
						found = True
						needsUpdate = False
						if not "XP" in y:
							y["XP"] = self.getServerStat(server, "DefaultXP")
							needsUpdate = True
						if not "XPReserve" in y:
							y["XPReserve"] = self.getServerStat(server, "DefaultXPReserve")
							needsUpdate = True
						if not "ID" in y:
							y["ID"] = user.id
							needsUpdate = True
						if not "Discriminator" in y:
							y["Discriminator"] = user.discriminator
							needsUpdate = True
						if not "Name" in y:
							y["Name"] = user.name
							needsUpdate = True
						if not "DisplayName" in y:
							y["DisplayName"] = user.display_name
							needsUpdate = True
						if not "Parts" in y:
							y["Parts"] = ""
							needsUpdate = True
						if not "Muted" in y:
							y["Muted"] = "No"
							needsUpdate = True
						if not "LastOnline" in y:
							y["LastOnline"] = None
							needsUpdate = True
						if not "Cooldown" in y:
							y["Cooldown"] = None
							needsUpdate = True
				if not found:
					needsUpdate = True
					# We didn't locate our user - add them
					newUser = { "Name" 			: user.name,
								"DisplayName" 	: user.display_name,
								"XP" 			: self.getServerStat(server, "DefaultXP"),
								"XPReserve" 	: self.getServerStat(server, "DefaultXPReserve"),
								"ID" 			: user.id,
								"Discriminator" : user.discriminator,
								"Parts"			: "",
								"Muted"			: "No",
								"LastOnline"	: "Unknown" }
					x["Members"].append(newUser)
				if needsUpdate:
					self.flushSettings()

	# Let's make sure the user is in the specified server
	def removeUser(self, user, server):
		# Make sure our server exists in the list
		self.checkServer(server)
		# Check for our username
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == user.id:
						found = True
						# Found our user - remove
						x["Members"].remove(y)
		if found:
			self.flushSettings()


	# Let's make sure the user is in the specified server
	def removeUserID(self, id, server):
		# Make sure our server exists in the list
		self.checkServer(server)
		# Check for our username
		found = False
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == id:
						found = True
						# Found our user - remove
						x["Members"].remove(y)
		if found:
			self.flushSettings()

	
	# Return the requested stat
	def getUserStat(self, user, server, stat):
		# Make sure our user and server exists in the list
		self.checkUser(user, server)
		# Check for our username
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == user.id:
						# Found our user - now check for the stat
						if stat in y:
							# Stat exists - return it
							return y[stat]
						else:
							# Stat does not exist - return None
							return None
		# If we were unable to add/find the user (unlikely), return None
		return None
	
	
	# Set the provided stat
	def setUserStat(self, user, server, stat, value):
		# Make sure our user and server exists in the list
		self.checkUser(user, server)
		# Check for our username
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == user.id:
						# Found our user - let's set the stat
						y[stat] = value
						self.flushSettings()
						
					
	# Increment a specified user stat by a provided amount
	# returns the stat post-increment, or None if error
	def incrementStat(self, user, server, stat, incrementAmount):
		# Make sure our user and server exist
		self.checkUser(user, server)
		# Check for our username
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server, now to iterate users
				for y in x["Members"]:
					if y["ID"] == user.id:
						# Found our user - check for stat
						if stat in y:
							# Found
							tempStat = int(y[stat])
							tempStat += int(incrementAmount)
							y[stat] = tempStat
							self.flushSettings()
							return tempStat
						else:
							# No stat - set stat to increment amount
							y[stat] = incrementAmount
							self.flushSettings()
							return incrementAmount
		# If we made it here - we failed somewhere, return None
		return None
	
	
	# Get the requested stat
	def getServerStat(self, server, stat):
		# Make sure our server exists in the list
		self.checkServer(server)
		# Check for our server
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# Found the server, check for the stat
				if stat in x:
					return x[stat]
				else:
					return None
		# Server was not located - return None
		return None
	
	
	# Set the provided stat
	def setServerStat(self, server, stat, value):
		# Make sure our server exists in the list
		self.checkServer(server)
		# Check for our server
		for x in self.serverDict["Servers"]:
			if x["ID"] == server.id:
				# We found our server - set the stat
				x[stat] = value
				self.flushSettings()

	
	@commands.command(pass_context=True)
	async def owner(self, ctx, member : discord.Member = None):
		"""Sets the bot owner - once set, can only be changed by the current owner."""
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel

		if member == None:
			member = author

		if type(member) is str:
			try:
				member = discord.utils.get(server.members, name=member)
			except:
				print("That member does not exist")
				return

		try:
			owner = self.serverDict['Owner']
		except KeyError:
			owner = None

		if owner == None:
			# No previous owner, let's set them
			self.serverDict['Owner'] = member.id
			self.flushSettings()
		else:
			if not author.id == owner:
				msg = 'You are not the *true* owner of me.  Only the rightful owner can change this setting.'
				await self.bot.send_message(channel, msg)
				return
			self.serverDict['Owner'] = member.id
			self.flushSettings()

		msg = 'I have been claimed by *{}!*'.format(DisplayName.name(member))
		await self.bot.send_message(channel, msg)

	@owner.error
	async def owner_error(ctx, error):
		msg = 'owner Error: {}'.format(ctx)
		await self.bot.say(msg)


	@commands.command(pass_context=True)
	async def disown(self, ctx):
		"""Revokes ownership of the bot."""
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel

		try:
			owner = self.serverDict['Owner']
		except KeyError:
			owner = None

		if owner == None:
			# No previous owner, let's set them
			msg = 'I have already been disowned...'
			await self.bot.send_message(channel, msg)
			return
		else:
			if not author.id == owner:
				msg = 'You are not the *true* owner of me.  Only the rightful owner can disown me.'
				await self.bot.send_message(channel, msg)
				return
			self.serverDict['Owner'] = None
			self.flushSettings()

		msg = 'I have been disowned by *{}!*'.format(DisplayName.name(author))
		await self.bot.send_message(channel, msg)


	@commands.command(pass_context=True)
	async def getstat(self, ctx, stat : str = None, member : discord.Member = None):
		"""Gets the value for a specific stat for the listed member (case-sensitive)."""
		
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel
		
		if member == None:
			member = author

		if str == None:
			msg = 'Usage: `$getstat [stat] [member]`'
			await self.bot.send_message(channel, msg)
			return

		if type(member) is str:
			try:
				member = discord.utils.get(server.members, name=member)
			except:
				print("That member does not exist")
				return

		if member is None:
			msg = 'Usage: `$getstat [stat] [member]`'
			await self.bot.send_message(channel, msg)
			return

		try:
			newStat = self.getUserStat(member, server, stat)
		except KeyError:
			msg = '"{}" is not a valid stat for *{}*'.format(stat, DisplayName.name(member))
			await self.bot.send_message(channel, msg)
			return

		msg = '**{}** for *{}* is *{}!*'.format(stat, DisplayName.name(member), newStat)
		await self.bot.send_message(channel, msg)

	# Catch errors for stat
	@getstat.error
	async def getstat_error(ctx, error):
		msg = 'getstat Error: {}'.format(ctx)
		await self.bot.say(msg)
		

	@commands.command(pass_context=True)
	async def setsstat(self, ctx, stat : str = None, value : str = None):
		"""Sets a server stat (admin only)."""
		
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel
		
		isAdmin = author.permissions_in(ctx.message.channel).administrator
		# Only allow admins to change server stats
		if not isAdmin:
			await self.bot.send_message(channel, 'You do not have sufficient privileges to access this command.')
			return

		if stat == None or value == None:
			msg = 'Usage: $setsstat Stat Value'
			await self.bot.send_message(channel, msg)
			return

		self.setServerStat(server, stat, value)

		msg = '**{}** set to *{}!*'.format(stat, value)
		await self.bot.send_message(channel, msg)


	@commands.command(pass_context=True)
	async def getsstat(self, ctx, stat : str = None):
		"""Gets a server stat (admin only)."""
		
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel
		
		isAdmin = author.permissions_in(channel).administrator
		# Only allow admins to change server stats
		if not isAdmin:
			await self.bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return

		if stat == None:
			msg = 'Usage: `$getsstat [stat]`'
			await self.bot.send_message(ctx.message.channel, msg)
			return

		value = self.getServerStat(server, stat)

		msg = '**{}** is currently *{}!*'.format(stat, value)
		await self.bot.send_message(channel, msg)
		
	@commands.command(pass_context=True)
	async def flush(self, ctx):
		"""Flush the bot settings to disk (admin only)."""
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		# Only allow admins to change server stats
		if not isAdmin:
			await self.bot.send_message(ctx.message.channel, 'You do not have sufficient privileges to access this command.')
			return
		# Flush settings
		self.flushSettings()
		msg = 'Flushed settings to disk.'
		await self.bot.send_message(ctx.message.channel, msg)
				
				
	# Flush settings to disk
	def flushSettings(self):
		json.dump(self.serverDict, open(self.file, 'w'), indent=2)

	@commands.command(pass_context=True)
	async def prunelocalsettings(self, ctx):
		"""Compares the current server's settings to the default list and removes any non-standard settings (owner only)."""

		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel

		try:
			owner = self.serverDict['Owner']
		except KeyError:
			owner = None

		if owner == None:
			# No previous owner, let's set them
			msg = 'I have not been claimed, *yet*.'
			await self.bot.send_message(channel, msg)
			return
		else:
			if not author.id == owner:
				msg = 'You are not the *true* owner of me.  Only the rightful owner can use prune.'
				await self.bot.send_message(channel, msg)
				return

		removedSettings = 0
		settingsWord = "settings"

		for serv in self.serverDict["Servers"]:
			if serv["ID"] == server.id:
				# Found it - let's check settings
				removeKeys = []
				for key in serv:
					if not key in self.defaultServer:
						if key == "Name" or key == "ID":
							continue
						# Key isn't in default list - clear it
						removeKeys.append(key)
						removedSettings += 1
				for key in removeKeys:
					serv.pop(key, None)

		if removedSettings is 1:
			settingsWord = "setting"
		
		msg = 'Pruned *{} {}*.'.format(removedSettings, settingsWord)
		await self.bot.send_message(ctx.message.channel, msg)
		# Flush settings
		self.flushSettings()


	@commands.command(pass_context=True)
	async def prunesettings(self, ctx):
		"""Compares all connected servers' settings to the default list and removes any non-standard settings (owner only)."""

		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel

		try:
			owner = self.serverDict['Owner']
		except KeyError:
			owner = None

		if owner == None:
			# No previous owner, let's set them
			msg = 'I have not been claimed, *yet*.'
			await self.bot.send_message(channel, msg)
			return
		else:
			if not author.id == owner:
				msg = 'You are not the *true* owner of me.  Only the rightful owner can use prune.'
				await self.bot.send_message(channel, msg)
				return

		removedSettings = 0
		settingsWord = "settings"

		for serv in self.serverDict["Servers"]:
			# Found it - let's check settings
			removeKeys = []
			for key in serv:
				if not key in self.defaultServer:
					if key == "Name" or key == "ID":
						continue
					# Key isn't in default list - clear it
					removeKeys.append(key)
					removedSettings += 1
			for key in removeKeys:
				serv.pop(key, None)

		if removedSettings is 1:
			settingsWord = "setting"
		
		msg = 'Pruned *{} {}*.'.format(removedSettings, settingsWord)
		await self.bot.send_message(ctx.message.channel, msg)
		# Flush settings
		self.flushSettings()


	@commands.command(pass_context=True)
	async def prune(self, ctx):
		"""Iterate through all members on all connected servers and remove orphaned settings (owner only)."""
		
		author  = ctx.message.author
		server  = ctx.message.server
		channel = ctx.message.channel

		try:
			owner = self.serverDict['Owner']
		except KeyError:
			owner = None

		if owner == None:
			# No previous owner, let's set them
			msg = 'I have not been claimed, *yet*.'
			await self.bot.send_message(channel, msg)
			return
		else:
			if not author.id == owner:
				msg = 'You are not the *true* owner of me.  Only the rightful owner can use prune.'
				await self.bot.send_message(channel, msg)
				return
		
		# Set up vars
		removedUsers = 0
		removedChannels = 0
		removedServers = 0
		channelWord = "channels"
		serverWord = "servers"
		usersWord = "users"

		for botServer in self.serverDict["Servers"]:
			# Let's check through each server first - then members
			foundServer = False
			for serve in self.bot.servers:
				# Check ID in case of name change
				if botServer["ID"] == serve.id:
					foundServer = True
					# Now we check users...
					for botMember in botServer["Members"]:
						foundMember = False
						for member in serve.members:
							if botMember["ID"] == member.id:
								foundMember = True
							
						if not foundMember:
							# We didn't find this member - remove them
							self.removeUserID(botMember['ID'], serve)
							removedUsers +=1

					for botChannel in botServer["ChannelMOTD"]:
						foundChannel = False
						for chan in serve.channels:
							if botChannel['ID'] == chan.id:
								foundChannel = True
						
						if not foundChannel:
							# We didn't find this channel - remove
							self.removeChannelID(botChannel['ID'], serve)
							removedChannels += 1
						
			if not foundServer:
				# We didn't find this server - remove it
				self.removeServerID(botServer['ID'])
				removedServers += 1

		if removedServers is 1:
			serverWord = "server"
		if removedChannels is 1:
			channelWord = "channel"
		if removedUsers is 1:
			usersWord = "user"
		
		msg = 'Pruned *{} {}*, *{} {}*, and *{} {}*.'.format(removedUsers, usersWord, removedChannels, channelWord, removedServers, serverWord)
		await self.bot.send_message(ctx.message.channel, msg)
