import os
import MyResult

import requests
import urllib2
import urllib 

def session () :
    ""

class MyResult :

  def __init__(self, content):
#    print "content:%s\n" % content
    self.content = content

class MyArgs :
  def __init__(self):
    ''
  def get (self, name, default= 0 ) :
#    print "args get name %s\n" % name
    return "name"
  

def graph_server () :
  #graph_server= 'http://127.0.0.1:5002' # local graph.facebook.com
  return 'http://127.0.0.1:5002/graph'

def facebook_server () :
  #facebook_server= 'http://127.0.0.1:5002' # local www.facebook.com
  return 'http://127.0.0.1:5002/facebook' # local www.facebook.com



def get (url, params=None) :

  if (params is not None):


    for k, v in params.iteritems():
      params[k] = "".join(params[k])
#      print "Check:" +  k 
#      print "Value" + "".join(params[k])
      #argsurl = argsurl + k + "=" + 

#            params[k] = v.encode('utf-8')
    argsurl = urllib.urlencode(  params)
    url = url + '?' +argsurl

  print "get url %s\n" % url
  data = urllib2.urlopen(url).read()
  return MyResult(data)
#  return MyResult(content)

#def __init__ (self) :
#  self.args = MyArgs()
args = MyArgs()

host = "127.0.0.1"
