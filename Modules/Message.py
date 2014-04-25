import ZODB
from persistent import Persistent
from persistent import list

class GMessage(Persistent):
	def __init__(self,messageId,jid,author,content,timestamp,receiptRequested,pushName):
		print "New message %s" % jid
		print content
		self.messageId=messageId
		self.jid=jid
		self.author=author
		self.content=content
		self.timestamp=timestamp
		self.receiptRequested=receiptRequested
		self.pushName=pushName
		self.type="group"

class Message(Persistent):
	def __init__(self,messageId,jid,content,timestamp,receiptRequested):
		print "New message %s" % jid
		print content
		self.messageId=messageId
		self.jid=jid
		self.content=content
		self.timestamp=timestamp
		self.receiptRequested=receiptRequested
		self.type="individual"

class OMessage(Persistent):
	def __init__(self,messageId,jid,content,timestamp):
		print "Outgoing message %s" % jid
		print content
		self.messageId=messageId
		self.jid=jid
		self.content=content
		self.timestamp=timestamp
		#self.receiptRequested=receiptRequested
		self.type="out"
