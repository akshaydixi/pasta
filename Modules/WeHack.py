import urllib
from bs4 import BeautifulSoup
class WeHackBot():
  def __init__(self):
    self.site = 'http://clabhacks.com/details.php'

  def count(self):
    try:
        sock = urllib.urlopen(self.site)
        content = sock.read()
        sock.close()
        soup = BeautifulSoup(content)
        trs = soup.findAll('tr')
        soup = BeautifulSoup(str(trs[-1]))
        tds = soup.findAll('td')
        firsttd = tds[0]
        sock = urllib.urlopen('http://clabs.vit.ac.in/wehackcount')
        content = sock.read()
        sock.close()
        return {"text" : str(eval(firsttd.string) + eval(content)) + " registrations so far!"}
    except:
      return {"error" : "404 - Site down"}
