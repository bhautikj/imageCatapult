#
#  Copyright (c) 2013 Bhautik J Joshi (bjoshi@gmail.com)
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

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
