import urllib2

class contentError(Exception):
 def __init__(self, value):
  self.value = value
 def __str__(self):
  return(repr(self.value))

try:
 url = 'http://localhost/healthcheck.html'
 pageContent = urllib2.urlopen(url).read().rstrip()
 if str(pageContent) =='healthy':
  exit(0)
 else:
  raise(contentError(pageContent))
except urllib2.HTTPError as e:
 print('There was a HTTP. Error: ',e.value)
 exit(1)
except urllib2.URLError as e:
 print('There was an error opening the URL. Error: ',e.value)
 exit(1)
except contentError as e:
 print('The content of the healthcheck did not match. Expected Content-"healthy", we got: ' + e.value)
 exit(1)
except:
 raise
 exit(1)
