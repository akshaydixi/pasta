from Pokemon import PokemonBot
from Keywords import Keywords
from WeHack import WeHackBot
import base64
import urllib
import os
import hashlib
START_DELIMITER_SYMBOL = '!'

class Bot():

  def __init__(self):
    self.jid = None
    self.name = None
    self.size = None
    self.base64_string = None
    self.mI = None
  def upload(self,url,methodsInterface,MediaUploader):
    print self.jid,self.name,self.size
    print url
    self.mI = methodsInterface
    theUploader = MediaUploader(self.jid,"919414105777@s.whatsapp.net",self.uploadFinally,self.uploadFailed)
    print "Uploader initialized!!!"
    theUploader.upload("/home/akshay/yetAnotherWorkspace/pasta/image.png",url)
  def uploadFinally(self,url):
    self.mI.call("message_imageSend",(self.jid,url,self.name,str(self.size),self.base64_string))

  def uploadFailed(self):
    print "Upload Failed!!!!!"

  def uploadDuplicate(self,url,methodsInterface):
    methodsInterface.call('message_imageSend',(self.jid,url,self.name,str(self.size),self.base64_string))
  def message(self, content, methodsInterface,jid):
    if content[0] == START_DELIMITER_SYMBOL:
      parts = content[1:].split()
      parts = [ part.lower() for part in parts]
      keyword = parts[0]
      command = parts[1]
      try:
        params = parts[2:]
      except:
        params = ['']

      ## Pokemon Bot stuff here ##

      if keyword == 'pokemon':
        pokebot = PokemonBot()
        if command  == 'pic' or command == 'image':
          result = pokebot.image(params[0])
        if command == 'desc' or command == 'description':
          result = pokebot.description(params[0])
      if keyword == 'wehack':
        wehackbot = WeHackBot()
        if command == 'count' or command == 'registrations':
         result = wehackbot.count()
      # Wiki stuff here ##
      #if keyword == 'wiki':



      print "Result : ",result
      for r in result:
        if r=='text':
          content = str(result[r])
          methodsInterface.call("message_send",(jid,content))
        if r == 'image':
          url = str(result[r])
          print url
          self.jid = jid
          self.name = params[0]
          urllib.urlretrieve(url,"image.png")
          self.size = os.stat("image.png").st_size
          fp = open("image.png","rb")
          sha1 = hashlib.sha256()
          sha1.update(fp.read())
          hsh = base64.b64encode(sha1.digest())
          methodsInterface.call("media_requestUpload",(hsh,"image",self.size))
          with open("image.png","rb")  as image_file:
              self.base64_string = base64.b64encode(image_file.read())

        if r == 'error':
          content = str(result[r])
          methodsInterface.call("message_send",(jid,content))
          #print hsh,self.base64_string
          #print base64_string
          #methodsInterface.call("message_imageSend",(jid,url,"Image",str(size),base64_string))
    #methodsInterface.call("message_send",(jid,content))

