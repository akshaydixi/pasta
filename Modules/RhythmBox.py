import os
import commands
class RhythmBoxBot():
  def __init__(self):
    pass

  def play(self):
    try:
      os.system("rhythmbox-client --play")
#return {}
    except:
      return {"error" : "Cannot initiate music player! Call Akshay!"}

  def pause(self):
    try:
      os.system("rhythmbox-client --pause")
 #     return {}
    except:
      return {"error" : "Cannot initiate music player! Call Akshay!"}

  def next(self):
    try:
      os.system("rhythmbox-client --next")
  #    return {}
    except:
      return {"error" : "Cannot initiate music player! Call Akshay!"}

  def previous(self):
    try:
      os.system("rhythmbox-client --previous")
   #   return {}
    except:
      return {"error" : "Cannot initiate music player! Call Akshay!"}

  def current(self):
    try:
      current = commands.getoutput("rhythmbox-client --print-playing")
      return {"text" : current}
    except:
      return {"error" : "Cannot initiate music player! Call Akshay!"}

  def help(self):
      helpstring = "Commands supported are : play, pause, next, previous, volume and current"
      return {"text":helpstring}

  def volume(self,volume):
    try:
      os.system("rhythmbox-client --set-volume " + str(volume))
    except:
      return {"error": "Cannot initiate music player! Call Akshay!"}
