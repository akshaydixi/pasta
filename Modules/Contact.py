import ZODB
from persistent import Persistent
from persistent import list

class Contact(Persistent):
	def __init__(self,jid):
		print "New person %s" % jid
		self.jid=jid
		self.messages=list.PersistentList()
		self.type="individual"
	def setname(self, pushName):
		self.name = pushName 
	def setstatus(self, status):
		self.status=status	
	def messageAdd(self,messageId):
		self.messages.append(messageId)
	def setNick(self,nick):
		self.nick=nick
	def setLastSeen(self,lastSeen):
		self.lastSeen=lastSeen
