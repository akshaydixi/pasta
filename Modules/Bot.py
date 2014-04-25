from Pokemon import PokemonBot

class Bot():
  def __init__(self):
    pass

  def message(self, content, methodsInterface):
    methodsInterface.call("message_send",("919566816614@s.whatsapp.net",content))
