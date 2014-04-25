import ZODB
from persistent import Persistent
from persistent import list

class Group(Persistent):
	def __init__(self,jid):
		print "New group %s" % jid
		self.jid=jid
		self.participants=list.PersistentList()
		self.messages=list.PersistentList()
		self.type="group"
	def setOwner(self, owner):
		self.owner = owner
	def setSubject(self, subject):
		self.subject=subject
	def setSubjectOwner(self,subjectOwner):
		self.subjectOwner=subjectOwner
	def setSubjectTimestamp(self,subjectTimestamp):
		self.subjectTimestamp=subjectTimestamp
	def setCreationTimestamp(self,creationTimestamp):
		self.creationTimestamp=creationTimestamp
	def setParticipants(self,jids):
		self.participants=jids	
	def messageAdd(self,messageId):
		self.messages.append(messageId)
	def setNick(self,nick):
		self.nick=nick
	
