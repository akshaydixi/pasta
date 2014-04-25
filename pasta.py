from Yowsup.connectionmanager import *
from auth import phone,password
import base64
password = base64.b64decode(bytes(password.encode('utf-8')))
import serial,codecs,time
from Modules.Bot import Bot



SERIALCONTENT = "pasta - a whatsappbot"

def makeJid(phone):
  return phone+'@s.whatsapp.net'

def onAuthSuccess(ph):
  print "Logged in with %s" % ph

def onMessageReceived(messageId,jid,content,timestamp,receiptRequested,x,y):
  global SERIALCONTENT,pastabot
  methodsInterface.call("message_ack",(jid,messageId))
  SERIALCONTENT = content.encode(sys.stdout.encoding,errors='replace')
  print SERIALCONTENT
  pastabot = Bot()
  pastabot.message(SERIALCONTENT,methodsInterface)
  
  """
  if len(SERIALCONTENT) < 16:
    ser.write(SERIALCONTENT)
  """

def onGroupSubjectReceived(messageId,jid,author,subject,timestamp,receiptRequeted):
  global SERIALCONTENT
  methodsInterface.call("subject_ack",(jid,messageId))
  SERIALCONTENT = subject.encode(sys.stdout.encoding, errors='replace')
  print SERIALCONTENT
  """
  if len(SERIALCONTENT) <  16:
    ser.write(SERIALCONTENT)
  """

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
signalsInterface.registerListener("receipt_messageSent", onMessageSent)
signalsInterface.registerListener("receipt_messageDelivered", onMessageDelivered)
signalsInterface.registerListener("group_subjectReceived",onGroupSubjectReceived)

signalsInterface.registerListener("ping",onPing)
methodsInterface.call("ready")
#ser = serial.Serial('/dev/ttyUSB0',9600)

while True:
  s = raw_input("Enter message: ")
  methodsInterface.call("message_send",("919566816614@s.whatsapp.net",s))
  """
  if len(SERIALCONTENT) > 16:
    times = len(SERIALCONTENT) - 15
    for i in range(times):
      ser.write(SERIALCONTENT[i:i+16])
      time.sleep(0.25)
  """

