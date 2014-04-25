from Yowsup.connectionmanager import *
from auth import phone,password
import base64
password = base64.b64decode(bytes(password.encode('utf-8')))

def makeJid(phone):
  return phone+'@s.whatsapp.net'

def onAuthSuccess(ph):
  print "Logged in with %s" % ph

def onMessageReceived(jid, messageId,content,timestamp,receiptRequested,x,y):
  methodsInterface.call("message_ack",(jid,messageId))
  print jid,messageId,content

def onMessageSent(jid,messageId):
  print "message sent successfully to %s" % jid

def onMessageDelivered(jid, messageId):
  print "Message delivered successfully to %s " % jid
  methodsInterface.call("delivered_ack",(jid,messageId))

def onPing(pingId):
  methodsInterface.call("pong", (pingId,))

def onReady():
  print "Ready?"

y = YowsupConnectionManager()
signalsInterface = y.getSignalsInterface()
methodsInterface = y.getMethodsInterface()
signalsInterface.registerListener("auth_success",onAuthSuccess)
methodsInterface.call("auth_login",(phone,password))
signalsInterface.registerListener("message_received",onMessageReceived)
signalsInterface.registerListener("recept_messageSent", onMessageSent)
signalsInterface.registerListener("receipt_messageDelivered", onMessageDelivered)
signalsInterface.registerListener("ping",onPing)
methodsInterface.call("ready")

while True:
  pass


