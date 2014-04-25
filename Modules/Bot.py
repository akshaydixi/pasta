'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import time, datetime, codecs, re, string

from Yowsup.connectionmanager import YowsupConnectionManager

import ZODB
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from Modules.myzodb import MyZODB, transaction
from Modules.Group import Group
from Modules.Message import Message,GMessage,OMessage
from Modules.Contact import Contact
from Modules.Response import Response
from Modules.wiki import wiki
from Modules.google import google


class Bot:
	
	def __init__(self, keepAlive = False, sendReceipts = True):
		self.sendReceipts = sendReceipts
		
		connectionManager = YowsupConnectionManager()
		connectionManager.setAutoPong(keepAlive)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("group_messageReceived", self.onGroupMessageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		self.signalsInterface.registerListener("presence_updated", self.onPresence_updated)
		self.signalsInterface.registerListener("presence_available", self.onPresence_available)
		self.signalsInterface.registerListener("presence_unavailable", self.onPresence_unavailable)
		
		self.signalsInterface.registerListener("contact_gotProfilePicture", self.onContact_gotProfilePicture)
		
		self.signalsInterface.registerListener("profile_setStatusSuccess", self.onProfile_setStatusSuccess)
		self.signalsInterface.registerListener("status_dirty", self.onStatus_dirty)
		
		self.signalsInterface.registerListener("contact_gotProfilePictureId", self.onContact_gotProfilePictureId)
		self.signalsInterface.registerListener("contact_gotProfilePicture", self.onContact_gotProfilePicture)
		
		self.signalsInterface.registerListener("group_gotParticipants", self.onGroup_gotParticipants)
		
		self.cm = connectionManager
		self.db = MyZODB('Data/Data.fs')
		self.dbroot = self.db.dbroot
		if not self.dbroot.has_key("groups"):
			self.dbroot["groups"] = PersistentMapping()
		if not self.dbroot.has_key("messages"):
			self.dbroot["messages"] = PersistentMapping()
		if not self.dbroot.has_key("config"):
			self.dbroot["config"] = PersistentMapping()
		if not self.dbroot.has_key("features"):
			self.dbroot["features"] = PersistentMapping()
		if not self.dbroot.has_key("contacts"):
			self.dbroot["contacts"] = PersistentMapping()
		if not self.dbroot.has_key("chats"):
			self.dbroot['chats'] = PersistentMapping()
		if not self.dbroot['features'].has_key("responses"):
			self.dbroot['features']['responses'] = PersistentMapping()
		if not self.dbroot['features'].has_key("outbox"):
			self.dbroot['features']['outbox'] = PersistentList()
		self.outbox=self.dbroot['features']['outbox']
		self.outboxempty=False
		self.outboxprocessing=False
		
	def login(self, username, password):
		self.username = username
		self.password=password
		pushName='fadbot'
		self.methodsInterface.call("auth_login", (username, password))
		self.methodsInterface.call("presence_sendAvailable",)
		print "online\n"
		while True:
			command=raw_input()
			if command=="/quit":
				transaction.commit()
				try:
					self.db.close()
				except KeyError:
					print "KeyError"
				break
			else:
				self.onCommand(command)
				continue
					
				
	def onCommand(self,command):
		if command.startswith("!"):
			splits=command.lstrip('!').split(' ',1)
			command=splits[0]
			try:
				rest=splits[1]
			except IndexError:
				rest=None
				
			if command=="status":
				status=rest
				self.profile_setStatus(status.encode('utf-8'))
			if command=="message":
				splits=rest.split(' ',1)
				if rest:
					recepient=splits[0]
					try:
						message=splits[1]
					except IndexError:
						message=raw_input("Enter the message: ")
				else:
					recepient=raw_input("Enter recepient nick or jid: ")
					message=raw_input("Enter the message: ")
				self.message_send(recepient,message)
			if command=="savelastcontact":
				lastcontact=self.dbroot['config']['lastchatwith']
				if rest:
					nick=rest
				else:
					nick=raw_input("what nick to give for %s: " % lastcontact)
				self.dbroot['chats'][lastcontact].setNick(nick)
				transaction.commit()
				print "%s saved as %s" % (lastcontact,nick)
			if command=="groupupdate":
				if rest:
					group=rest
				else:
					group=raw_input("Enter group jid: ")
				self.group_getParticipants(group)
			if command=="grouppics":
				if rest:
					group=rest
				else:
					group=raw_input("Enter group jid: ")
				self.picture_getIds(self.dbroot['chats'][group].participants)	
			if command=="savecontact":
				if rest:
					splits=rest.split()
					jid=splits[0]
					try:
						nick=splits[1]
					except IndexError:
						nick=raw_input("Enter nick: ")
				else:
					jid=raw_input("whom to give nick?: ")
					nick=raw_input("Enter nick: ")
				try:
					self.dbroot['chats'][jid].setNick(nick)
				except KeyError:
					if self.is_group(jid):
						self.dbroot['chats'][jid]=Group(jid)
					else:
						self.dbroot['chats'][jid]=Contact(jid)
					self.dbroot['chats'][jid].setNick(nick)
				transaction.commit()
				print "%s saved as %s" % (jid,nick)
			if command=="addresponse":
				splits=rest.split('|')
				prompt=splits[0]
				response=splits[1]
				try:
					alsoGroup=splits[2]
				except IndexError:
					alsoGroup=False
				self.addAIresponse(prompt,response,alsoGroup)
			if command=="aimode":
				try:
					aimode=self.dbroot['config']['aimode']
				except KeyError:
					self.dbroot['config']['aimode']=False
					aimode=False
				if rest:
					if rest=="on":
						aimode=True
					elif rest=="off":
						aimode=False
					else:
						print "aimode is currently %s " %  "on" if aimode else "off"
				else: 
					aimode=1-aimode
					print "aimode turned %s " % "on" if aimode else "off"
				print "aimode is currently %s" % "on" if aimode else "off"
		return
				
	def onAuthSuccess(self, username):
		print "Authed %s" % username
		self.methodsInterface.call("ready")

	def onAuthFailed(self, username, err):
		print "Auth Failed!"

	def onDisconnected(self, reason):
		print "Disconnected because %s" %reason
		if reason=="dns": time.sleep(30)
		time.sleep(1)
		self.login(self.username,self.password)

	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName,extra):
		messageContent=messageContent.decode('utf8')
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))		
		if not self.dbroot['chats'].has_key(jid):
			self.dbroot['chats'][jid]=Contact(jid)
		contact=self.dbroot['chats'][jid]
		
		contact.messageAdd(messageId)
		self.dbroot['messages'][messageId]=Message(messageId,jid,messageContent,timestamp,wantsReceipt)
		self.dbroot['config']['lastchatwith']=jid
		transaction.commit()
		
		self.AI("messageId",messageId)

		
	def onGroupMessageReceived(self, messageId, jid, msgauthor, messageContent, timestamp, wantsReceipt, pushName):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		messageContent=messageContent.decode('utf8')
		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))
		if not self.dbroot['chats'].has_key(jid):
			self.dbroot['chats'][jid]=Group(jid)
		group=self.dbroot['chats'][jid]
		
		group.messageAdd(messageId)
		self.dbroot['messages'][messageId]=GMessage(messageId,jid,msgauthor,messageContent,timestamp,wantsReceipt,pushName)
		self.dbroot['config']['lastchatwith']=jid
		transaction.commit()
		
		self.AI("messageId",messageId)
				
	def printstuff(jid):
		pass
		# Put something here to print everything
		
	def message_send(self,recepient, content):
		jid=self.findjidbynick(recepient)
		messageId = self.methodsInterface.call("message_send",(jid,content.encode('utf-8')))
		self.dbroot['messages'][messageId]=OMessage(messageId,jid,content,time.time())
		self.dbroot['chats'][jid].messageAdd(messageId)
		transaction.commit()
	
	def message_queue(self,recepient, content):
		newmessage=(recepient,content)
		self.outbox.append(newmessage)
		self.outboxempty=False
		self.process_messageQueue()
		
	def process_messageQueue(self):
		if (self.outboxempty or self.outboxprocessing):
			return
		else:
			self.outboxprocessing=True
			while ((len(self.outbox))!=0):
				x=self.outbox.pop(0)
				recepient,content=x
				self.methodsInterface.call("typing_send",(recepient,))
				time.sleep(1)
				self.message_send(recepient,content)
		self.outboxprocessing=False
		return
		
	
	def findjidbynick(self,recepient):
		for contact in self.dbroot['chats']:
			try:
				if self.dbroot['chats'][contact].nick==recepient:
					return contact
			except AttributeError:
				pass
		return recepient
	
	def is_group(self,jid):
		if '-' in jid:
			return True
		else:
			return False
	
	def AI(self,meta,data):
		#print "AI invoked"
		if meta=="messageId":
			#print "AI working on message"
			messageId=data
			message=self.dbroot['messages'][messageId]
			command=message.content
			mType=message.type
			if mType=="group":
				querer=message.pushName
				
		
			# message cross-over change this if you want messages from one group to go to another group and vice versa
			# maybe to extend group chat to 100?
			group1="918123148720-1340777161@g.us"
			group2="918123148720-1376840084@g.us"
			if message.jid==group1:
				recepient=group2
				self.crossMessage(recepient,message)
				return
			if message.jid==group2:
				recepient=group1
				self.crossMessage(recepient,message)
				return
			
			# manage generic commands
			if command.startswith("!"):
				command=command.lstrip('!')
				splits=command.split(' ',1)
				try:
					initcommand=splits[0]
				except IndexError:
					initcommand=None
				try:
					rest=splits[1]
				except IndexError:
					rest=None
				if initcommand=="bot":
					splits=rest.split(' ',1)
					botcommand=splits[0]
					rest=splits[1]
					if botcommand=="addresponse":
						splits=rest.split('|')
						prompt=splits[0]
						response=splits[1]
						try:
							alsoGroup=splits[2]
						except IndexError:
							alsoGroup=False
						self.addAIresponse(prompt,response,alsoGroup)
						return
				
				
			#if self.dbroot['config']['aimode']==True:
			if True: #set this to false to disable aimode
				originalText=command
				splits=command.split(' ',1)
				command=splits[0]
				command=command.lower()
				try: 
					rest=splits[1]
				except IndexError:
					rest=None
				#print "AI going to extermities"
				if command=="wiki":
					if rest:
						wikiresult=wiki(rest)
					else:
						wikiresult='You can actually make me search wikipedia by typing "wiki <search term>"'
					if mType=="group":
						reply="%s: %s" % (querer,wikiresult)
					else:
						reply=wikiresult
					self.message_queue(message.jid,reply.decode('utf-8'))
				elif command=="google":
					if rest:
						googleresult=google(rest)
					else:
						googleresult='make me search google by typing "google <search term>"'
					if mType=="group":
						reply="%s: %s" % (querer,googleresult)
					else:
						reply=googleresult
					self.message_queue(message.jid,reply.decode('utf-8'))
				
				elif mType=="individual":
					originalText=originalText.lower()
					strippedText="".join([c for c in originalText if c in string.letters or c in string.digits])
					responses=self.dbroot['features']['responses']
					print strippedText
					if responses.has_key(strippedText):
						self.message_queue(message.jid,responses[strippedText].response)
					else:
						self.message_queue(message.jid,"Oh oh :(")
			
	def addAIresponse(self,prompt,response,alsoGroup=False):
		fullprompt=prompt.lower()
		#pattern = re.compile('[\W_]+',re.UNICODE) 
    		#prompt=pattern.sub('', string.printable)
    		prompt="".join([c for c in fullprompt if c in string.letters or c in string.digits])
		newResponse=Response(prompt,response,alsoGroup)
		self.dbroot['features']['responses'][prompt]=newResponse
		#print "added response %s for prompt %s" % (newResponse.response,newResponse.prompt) 
		transaction.commit()
		
			
	def crossMessage(self,recepient,message):
		content=message.content
		pushName=message.pushName
		forward=content+"\n~%s" % pushName
		self.message_queue(recepient,forward)
		
	def typing_send(jid):
		pass
	def typing_paused(jid):
		pass
	
	#groups
	def group_getInfo(self,jid):
		self.methodsInterface.call("group_getInfo",(jid))
	
	def onGroup_gotInfo(self,jid,owner,subject,subjectOwner,subjectTimestamp,creationTimestamp):
		if not self.dbroot['chats'].has_key(jid):
			self.dbroot['chats'][jid]=Group(jid)
		group=self.dbroot['chats'][jid]
		group.setOwner(owner)
		group.setSubject(subject)
		group.setSubjectOwner(subjectOwner)
		group.setSubjectTimestamp(subjectTimestamp)
		group.setCreationTimestamp(creationTimestamp)
		transaction.commit()
	
	def onPresence_updated(self,jid, lastSeen):
		self.dbroot['chats'][jid].setLastSeen(lastSeen)
		transaction.commit()
	def onPresence_available(self,jid):
		pass
	def onPresence_unavailable(self,jid):
		pass
	
	def profile_setStatus(self,status):
		self.methodsInterface.call("profile_setStatus",(status,))	
	
	def onProfile_setStatusSuccess(self,jid,messageId):
		print "set the status of %s succesfully (%s)" % (jid, messageId)
		self.notification_ack(jid,messageId)
		
		
	def onStatus_dirty(self):
		print "dirty status"
		
		
	def notification_ack(self, jid, messageId):
		self.methodsInterface.call("notification_ack",(jid,messageId))
		
	def onContact_gotProfilePictureId(self,jid,pictureId):
		print "got dp Id of %s = %s" % (jid, pictureId)
			
	def onContact_gotProfilePicture(self,jid,filePath):
		print "got Profile Picture of %s = %s" % jid, filePath
	
	def contact_getProfilePicture(self,jid):
		self.methodsInterface.call("contact_getProfilePicture",(jid,))
	
	def picture_getIds(self,jids):
		self.methodsInterface.call("picture_getIds",(jids,))
		print "asking for pictures of %s" % jids
	
	def group_getParticipants(self,jid):
		self.methodsInterface.call("group_getParticipants",(jid,))
		print "asking for participants of %s" % jid
		
	def onGroup_gotParticipants(self,jid,jids):
		self.dbroot['chats'][jid].setParticipants(jids)
		transaction.commit()
		print "learned that %s is %s"% (jid,jids)
		
