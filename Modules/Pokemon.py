import pykemon
from random import choice

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

class PokemonBot():
  def __init__(self):
    pass

  def image(self,param):
    if is_number(param):
      try:
        url = pykemon.get(sprite=int(param)).image
        return {'image' : 'http://pokeapi.co/' + url}
      except:
        return {'error' : '404 - Wrong pokemon id'}
    else:
      try:
        pid = str(pykemon.get(pokemon=param).id)
        return {'image' : 'http://pokeapi.co//media/img/' + pid + '.png'}
      except:
        return {'error' : '404 - Wrong pokemon name'}

  def description(self,param):
	try:
		pokemon = pykemon.get(pokemon=param)
		description = choice(pokemon.descriptions.values())[:-1]
		num = description.split('/')[-1]
		description_text = pykemon.get(description=num).description
		return {'text' : description_text }
	except e:
		return {'error' : '404 - Wrong Pokemon query'}
          
        
      


  
