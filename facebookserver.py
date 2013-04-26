from flask import Flask
app = Flask(__name__)
from flask import request
import urllib2

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/facebook/oauth/access_token")
def oauth_access_token() :
    #?code=name&client_secret=12345&redirect_uri=https://127.0.0.1/&method=GET&client_id=123
    return "a=b&access_token=123&expires=123"

@app.route("/graph/<appid>")
def app_config(appid):
    return "{ \n \"name\" : \"some random app\", \n \"app_id\" : \"" + appid + "\"\n}"

@app.route("/graph/me/likes")
def graph_me_likes():
#    return "{ \n}"
    f = open('cache/mylikes.json', 'r')
    return f.read()

@app.route("/graph/me/friends")
def graph_me_friends():
#    return "{ \n}"
    f = open('cache/myfriends.json', 'r')
    return f.read()

@app.route("/graph/search")
def graph_search():
    print "graph search Request Data:"
    if ('__after_id' in request.args) :
        return "{}"        
    if ('type' in request.args) :
        qtype=  urllib2.unquote(request.args['type'])
        qval= urllib2.unquote(request.args['q'])
        qval.replace(" ","_")
        qval.replace(",","_")
        print  "qtype:" +        qtype +  " qval:"+       qval
        if ((qtype is None) or (qval is None) )   :
            return "{}"       
        filename = 'cache/search_' + qtype + "_" +  qval + '.json'
        print "graph search Request Data:" + filename
        f = open(filename, 'r')
        return f.read()
    return "{ \"unknown\" : \"\1\" }"        

@app.route("/graph/me/photos")
def graph_me_photos():
    f = open('cache/myphotos.json', 'r')
    return f.read()

@app.route("/facebook/method/fql.query")
def fb_method_fql_query():
    print "fql query Request Data:"
    print request.args
    return "{}"

if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=5002)

