import findLibs
from flickrInterface import flickrObject
from flickrInterface import flickrAuthApp
from facebookInterface import facebookObject
from facebookInterface import facebookApp
from tumblrInterface import tumblrObject
from tumblrInterface import tumblrApp
from twitterInterface import twitterObject
from twitterInterface import twitterApp
import web

import json

urls = (
  '/flickrAuth', flickrAuthApp,
  '/facebookAuth', facebookApp,
  '/tumblrAuth', tumblrApp,
  '/twitterAuth', twitterApp,
  '', 'Auth',
)

render = web.template.render('templates/')

class Auth:   
  def GET(self, names=None):
    params = web.input()
    numParams = len(params.keys())
    if numParams == 1 and params.keys()[0] == "authStatus":
      retDict = {}
      retDict["flickr"]   = flickrObject.authorised
      retDict["facebook"] = facebookObject.authorised
      retDict["tumblr"]   = tumblrObject.authorised
      retDict["twitter"]  = twitterObject.authorised
      return json.dumps(retDict)
      
    status = {}

    flickrAuth = 'Unauthorized'
    if flickrObject.authorised:
      flickrAuth = 'Authorized'

    facebookAuth = 'Unauthorized'
    if facebookObject.authorised:
      facebookAuth = 'Authorized'

    tumblrAuth = 'Unauthorized'
    if tumblrObject.authorised:
      tumblrAuth = 'Authorized'

    twitterAuth = 'Unauthorized'
    if twitterObject.authorised:
      twitterAuth = 'Authorized'
      
    status["flickr"] = flickrAuth
    status["facebook"] = facebookAuth
    status["tumblr"] = tumblrAuth
    status["twitter"] = twitterAuth

    return render.authPage(status)
  
authApp = web.application(urls, locals())
