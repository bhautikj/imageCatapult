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
import authPickler
from apiToolsBase import OAuthObjectBase
from apiToolsBase import redirectToUrlText

import urllib2
import urlparse
import json

import web
from web import form

import facebook

class FacebookObject(OAuthObjectBase):
  def __init__(self):
    OAuthObjectBase.__init__(self)
    self.apiName = "facebook"

  def authPart1(self):
    auth_url = 'https://www.facebook.com/dialog/oauth?client_id=' + self.api_key + \
               '&redirect_uri=' + web.ctx.homedomain + '/auth/facebookAuth&scope=offline_access,publish_stream'
    return auth_url

  def authPart2(self, code):
    access_token_url = 'https://graph.facebook.com/oauth/access_token?client_id=' + self.api_key + \
                       '&redirect_uri=' + web.ctx.homedomain + '/auth/facebookAuth' + \
                       '&client_secret=' + self.api_secret + '&code=' + code

    pageGet = urllib2.urlopen(access_token_url).read()
    self.final_oauth_token = urlparse.parse_qs(pageGet)['access_token'][0]
    authDict = authPickler.getAuthDict(self.apiName)
    authDict["final_oauth_token"] = self.final_oauth_token
    authPickler.setAuthDict(self.apiName, authDict)
    self.authorised = True

    self.setupAPI()
    
    return redirectToUrlText(web.ctx.homedomain)

  def setupAPI(self):
    self.facebookGraph = facebook.GraphAPI(self.final_oauth_token)
    
  def postImagePost(self, jobDict):
    paramsDict = {}

    if jobDict["title"] != None:
      paramsDict["name"] = jobDict["title"]
    if jobDict["description"] != None:
      paramsDict["description"] = jobDict["description"]
      
    paramsDict["link"] = jobDict["flickrurl"]
    paramsDict["picture"] =jobDict["flickrImageThumbUrl"]

    self.facebookGraph.put_wall_post("",paramsDict)

#-------------------------------------------------------------------------------

urls = (
"", "FacebookAuth",
)

render = web.template.render('templates/')

facebookObject = FacebookObject()
facebookObject.setup()

class FacebookAuth:
  def GET(self, path=None):
    global facebookObject

    if not facebookObject.authorised:
      params  = web.input()
      if 'code' in params.keys():
        return facebookObject.authPart2(params['code'])

  def POST(self):
    params = web.input()
    global facebookObject
    if "submitInitial" in params.keys():
      apiKey = params["apiKey"]
      apiSecret = params["apiSecret"]
      
      facebookObject.setupApp(apiKey, apiSecret)
      redirectURL =  facebookObject.authPart1()

      return json.dumps({'redirectURL':redirectURL})


facebookApp = web.application(urls, locals())
