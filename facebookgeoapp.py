# -*- coding: utf-8 -*-

import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
import urlparse
from base64 import urlsafe_b64decode, urlsafe_b64encode


on_heroku = True

#if you want to run locally export RUN_LOCALLY_OUTSIDE_HEROKU=1

if 'RUN_LOCALLY_OUTSIDE_HEROKU' in os.environ:
    import MyRequests as facebook_request
    graph_server= facebook_request.graph_server() 
    facebook_server= facebook_request.facebook_server() 
    api_facebook_server = facebook_request.facebook_api_server() 

else:
    print "running on facebook"
    import requests
    import requests as facebook_request
    graph_server= "https://graph.facebook.com"
    facebook_server= "https://www.facebook.com"
    api_facebook_server = "https://api.facebook.com"
    on_heroku = False



from flask import Flask, request, redirect, render_template, url_for

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = facebook_request.session()
app_url = graph_server + '/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(facebook_request.get(app_url).content).get('name')
FB_APP_SECRET = os.environ.get('FACEBOOK_SECRET')

print "creating app from %s \n" % __name__
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')

def oauth_login_url(preserve_path=True, next_url=None):
    fb_login_uri = ( facebook_server + "/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s" %
                    (app.config['FB_APP_ID'], get_home()))
    if app.config['FBAPI_SCOPE']:
        fb_login_uri += "&scope=%s" % ",".join(app.config['FBAPI_SCOPE'])
    return fb_login_uri

def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))

def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')

def fbapi_get_string(path,
                     params=None, 
                     access_token=None,
                     encode_func=urllib.urlencode):
    print "fbapi_get_string: %s\n" % path
    """Make an API call"""
    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token
    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')
    url =  facebook_server + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    result = facebook_request.get(url).content
    return result


def fbapi_auth(code):
    print "fbapi_auth: %s\n" % code
    params = {'client_id': app.config['FB_APP_ID'],
              'redirect_uri': get_home(),
              'client_secret': app.config['FB_APP_SECRET'],
              'code': code}
    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)
    pairs = result.split("&")
#    print "Pairs : " 
#    print pairs
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    return (result_dict["access_token"], result_dict["expires"])

def fbapi_get_application_access_token(id):
    print "fbapi_get_application_access_token: %s\n" % id
    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials', client_id=id,
                    client_secret=app.config['FB_APP_SECRET']),
        )
    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token

def fql(fql, token, args=None):
    print "fql: %s\n" % fql
    if not args:
        args = {}
    args["query"], args["format"], args["access_token"] = fql, "json", token
    url = api_facebook_server + "/method/fql.query"
    r = facebook_request.get(url, params=args)
    return json.loads(r.content)

def fb_call(call, args=None):
    print "fb_call: %s\n" % call
    url = graph_server + "/{0}".format(call)
#    if (args is not None ) :
#        print "args:" 
#        print args
    r = facebook_request.get(url, params=args)
    content = r.content
    print "got content  :" + content
    return json.loads(content)



def get_home():
    return 'https://' + request.host + '/'

# collect all pages via json
def get_all(name, args):
    total = []
    local = fb_call(name, args)
    count  =1 
    while 'data' in local :
        for d in local['data'] :
            d['count']=count
            total = total + [d]
        if 'paging' not in local  :            
            break
        if 'next' not in local['paging']:
            break
        next = local['paging']['next']
        count = count + 1
        query = urlparse.parse_qs(urlparse.urlparse(next).query)
        args2 = dict(args.items()+query.items() )
        local = fb_call('search', args2)
    return total

def get_token():
    print "get_token\n"
    print "Args:" , request.args
    
    if 'RUN_LOCALLY_OUTSIDE_HEROKU' in os.environ:
        return fbapi_auth("1234")[0]
    
    if request.args.get('code', None):
        return fbapi_auth(facebook_request.args.get('code'))[0]

    cookie_key = 'fbsr_{0}'.format(FB_APP_ID)
    if cookie_key in request.cookies:
        c = request.cookies.get(cookie_key)
        encoded_data = c.split('.', 2)
        sig = encoded_data[0]
        data = json.loads(urlsafe_b64decode(str(encoded_data[1]) +
            (64-len(encoded_data[1])%64)*"="))
        if not data['algorithm'].upper() == 'HMAC-SHA256':
            raise ValueError('unknown algorithm {0}'.format(data['algorithm']))
        h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
        h.update(encoded_data[1])
        expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')
        if sig != expected_sig:
            raise ValueError('bad signature')
        code =  data['code']
        params = {
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'redirect_uri': '',
            'code': data['code']
        }
        from urlparse import parse_qs
        r = facebook_request.get( graph_server + '/oauth/access_token', params=params)
        token = parse_qs(r.content).get('access_token')
        return token

# find by lat lon
@app.route('/discover/ll/<paramLat>/<paramLon>/<paramRange>', methods=['GET', 'POST'])      
def discover_lat_lon(paramLat,paramLon,paramRange):
    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    local = []
    likes = {} # hash of likes
    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        likesd= get_all('me/likes', {'access_token': access_token})
        for l in likesd:
            likes[l['id']]=l['name']
        local = get_all('search', {
                'access_token': access_token,
                'type'  : 'place',
                'center' : paramLat + ',' + paramLon ,
                'distance': paramRange
                })                    
        for d in local:
            d['online']=1
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)
    for d in local:
        if d['id'] in likes :
            d['liked']=1
        else:
            d['liked']=0
    fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
    return render_template('local.html', app=fb_app, app_id=FB_APP_ID, token=access_token, local=local, likes=likes, me=me, name=FB_APP_NAME)

# find new pages not yet liked
@app.route('/discover/name/<paramLocationName>', methods=['GET', 'POST'])
def discover_name(paramLocationName):
    print "discover_name:%s\n" % paramLocationName
    access_token = get_token()

    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    local = []
    likes = {} # hash of likes

    print "access token: %s " % access_token

    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        likesd= get_all('me/likes', {'access_token': access_token})
        for l in likesd:
            likes[l['id']]=l['name']
        local = get_all('search', { 'access_token': access_token, 'type'  : 'page',   'q' : paramLocationName })
        for d in local:
            d['online']=1
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

    for d in local:
        if d['id'] in likes :
            d['liked']=1
        else:
            d['liked']=0
    fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
    return render_template('local.html', app=fb_app, app_id=FB_APP_ID, token=access_token, local=local, likes=likes, me=me, name=FB_APP_NAME)

# export locals to osm
@app.route('/local/export/osm/<paramName>', methods=['GET', 'POST'])
def osm_export(paramName):
    local = get_all('search', { 
                                'type'  : 'page',   
                                'q' : paramName ,
                                'fields' :  'id,name,location,website,phone'
                                })
    newid = -1
    local2=[]
    for d in local:
        d['osmid'] = newid
        newid = newid -1
        if ('location' in d):
            local2 = local2 + [d]
    return render_template('osm.xml', local=local2)

# export likes to an osm file
@app.route('/likes/export/osm', methods=['GET', 'POST'])
def likes():
    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    if access_token:
        newid = -1
        local2=[]
        # find all the liked pages
        local= get_all('me/likes', {'access_token': access_token,  'fields' :  'id,name,location,website' })
        newid = -1
        for d in local:
            d['osmid'] = newid
            newid = newid -1
            if ('location' in d):
                local2 = local2 + [d]
        return render_template('osm.html',  local=local2 )
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/', methods=['GET', 'POST'])
def index():
    print "Main\n"
    print "Home:" + get_home()
    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        likes = fb_call('me/likes',
                        args={'access_token': access_token, 'limit': 4})
        friends = fb_call('me/friends',
                          args={'access_token': access_token, 'limit': 4})
        photos = fb_call('me/photos',
                         args={'access_token': access_token, 'limit': 16})
        redir = get_home() + 'close/'
        POST_TO_WALL = (facebook_server + "/dialog/feed?redirect_uri=%s&"
                        "display=popup&app_id=%s" % (redir, FB_APP_ID))
        app_friends = fql(
            "SELECT uid, name, is_app_user, pic_square "
            "FROM user "
            "WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) AND "
            "  is_app_user = 1", access_token)
        SEND_TO = (facebook_server + '/dialog/send?'
                   'redirect_uri=%s&display=popup&app_id=%s&link=%s'
                   % (redir, FB_APP_ID, get_home()))
        url = request.url
        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token, likes=likes,
            friends=friends, photos=photos, app_friends=app_friends, app=fb_app,
            me=me, POST_TO_WALL=POST_TO_WALL, SEND_TO=SEND_TO, url=url,
            channel_url=channel_url, name=FB_APP_NAME)
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if app.config.get('FB_APP_ID') and app.config.get('FB_APP_SECRET'):
        app.run(host='0.0.0.0', port=port)
    else:
        print 'Cannot start application without Facebook App Id and Secret set'
