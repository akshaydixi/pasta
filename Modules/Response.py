import ZODB
from persistent import Persistent
from persistent import list

class Response(Persistent):
	def __init__(self,prompt,response,alsoGroup):
		print "New response %s for prompt %s" % (response,prompt)
		self.prompt=prompt
		self.response=response
		self.alsoGroup=alsoGroup
	
