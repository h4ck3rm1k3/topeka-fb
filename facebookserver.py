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


def getdata(name) :
    print  "Requested:%s\n" % name
    try:
        filename = 'cache/'+ name +'.json.private'
        f = open(filename, 'r')
        print  "Opened:%s\n" % filename
    except IOError:
        filename = 'cache/'+ name +'.json'
        f = open(filename, 'r')
        print  "Opened:%s\n" % filename
    return f.read()


@app.route("/graph/me")
def graph_me():
    return getdata('me')

@app.route("/graph/me/likes")
def graph_me_likes():
    return getdata('mylikes')

@app.route("/graph/me/friends")
def graph_me_friends():
    return getdata('myfriends')


@app.route("/graph/search")
def graph_search():
    print "graph search Request Data:"
    if ('__after_id' in request.args) :
        return "{}"        

#distance=10000&type=place&center=38.970645,-95.235959
    if ('distance' in request.args) :        
        qtype=  urllib2.unquote(request.args['type'])
        qcenter= urllib2.unquote(request.args['center'])
        qdistance= urllib2.unquote(request.args['distance'])
        return getdata('search_page_latlon')


    if ('type' in request.args) :
        qtype=  urllib2.unquote(request.args['type'])
        qval= urllib2.unquote(request.args['q'])
        qval.replace(" ","_")
        qval.replace(",","_")
        print  "qtype:" +        qtype +  " qval:"+       qval
        if ((qtype is None) or (qval is None) )   :
            return "{}"       
        filename = 'search_' + qtype + "_" +  qval 
        return getdata(filename)

    return "{ \"unknown\" : \"\1\" }"        

@app.route("/graph/me/photos")
def graph_me_photos():
    getdata('myphotos.json')


@app.route("/api/method/fql.query")
def fb_method_fql_query():
    print "fql query Request Data:"
    print request.args

    if (request.args['query'] =='SELECT current_location FROM user WHERE uid=me()'):
        filename = 'current_location'
        return getdata(filename)


    return "{}"

@app.route("/graph/<appid>")
def app_config(appid):
    filename = 'id_lookup_%s' % appid
    print "graph id lookup:" + filename
    return getdata(filename)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5002)

