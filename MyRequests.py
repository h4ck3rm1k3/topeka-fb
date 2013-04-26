import os
import MyResult
on_heroku = True

#if you want to run locally export RUN_LOCALLY_OUTSIDE_HEROKU=1

if 'RUN_LOCALLY_OUTSIDE_HEROKU' in os.environ:
  on_heroku = False

def session () :
    ""

class MyResult :

  def __init__(self, content):
    print "content:%s\n" % content
    self.content = content


#  def content () :
#    print "content:%s\n" % content
#    return _content

def get (url) :
  print "get url %s\n" % url
  if (url == "https://graph.facebook.com/123"):
#    return MyResult("{ 'name'   : 'standalone' }")
    return MyResult("{ }")
  else:
    return MyResult("")
