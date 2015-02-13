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

import json

import web
from web import form

import oauth2 as oauth
from tumblr import TumblrClient

class TumblrObject(OAuthObjectBase):
  def __init__(self):
    OAuthObjectBase.__init__(self)
    self.apiName = "tumblr"

  def authPart1(self):
    from tumblr.oauth import TumblrOAuthClient
    self.tumblr_oauth = TumblrOAuthClient(self.api_key, self.api_secret)

    auth_url = self.tumblr_oauth.get_authorize_url()

    return auth_url

  def authPart2(self, oauth_verifier):
    access_token = self.tumblr_oauth.get_access_token(oauth_verifier)

    print "Access key:", access_token.key
    print "Access Secret:", access_token.secret

    self.final_oauth_token = access_token.key
    self.final_oauth_token_secret = access_token.secret

    authDict = authPickler.getAuthDict(self.apiName)
    authDict["final_oauth_token"] = self.final_oauth_token
    authDict["final_oauth_token_secret"] = self.final_oauth_token_secret
    authPickler.setAuthDict(self.apiName, authDict)
    self.authorised = True

    self.setupAPI()

    return redirectToUrlText(web.ctx.homedomain)

  def setupAPI(self):
    hostname = self.publishURL
    consumer = oauth.Consumer(self.api_key, self.api_secret)
    token = oauth.Token(self.final_oauth_token, self.final_oauth_token_secret)
    self.tumblr = TumblrClient(hostname, consumer, token) 


  def postTestPost(self):
    params = {
      'type': 'text',
      'body': 'testPost'
    }
    json_response = self.tumblr.create_post(request_params=params)
    if json_response["meta"]["status"] != 201:
      print json_response
      raise Exception("Tumblr upload error!")   
    
  def postImagePost(self, jobDict):
    captionString = ""
    
    if jobDict["title"] != None:
      captionString = "<strong>" + jobDict["title"] + "</strong><br/>"
    if jobDict["description"] != None:
      captionString += jobDict["description"]
      
    params = {
        'type':'photo',
        'caption': captionString,
        'link': jobDict["flickrurl"],
        'source': jobDict["flickrImageLargeUrl"],
        'tags': ','.join(jobDict["tags"])
    }
        
    json_response = self.tumblr.create_post(request_params=params)
    if json_response["meta"]["status"] != 201:
      print "TUMBLR ERROR"
      print json_response
      raise Exception("Tumblr upload error!")
    
    
#-------------------------------------------------------------------------------

urls = (
"", "TumblrAuth",
)


render = web.template.render('templates/')

tumblrObject = TumblrObject()
tumblrObject.setup()

class TumblrAuth:
  def GET(self, path=None):
    global tumblrObject

    if not tumblrObject.authorised:
      params  = web.input()
      if 'oauth_verifier' in params.keys():
        return tumblrObject.authPart2(params['oauth_verifier'])

  def POST(self):
    params = web.input()
    global tumblrObject
    if "submitInitial" in params.keys():
      apiKey = params["apiKey"]
      apiSecret = params["apiSecret"]
      blogURL = params["blogURL"]
      
      tumblrObject.setupApp(apiKey, apiSecret, blogURL)
      redirectURL =  tumblrObject.authPart1()

      return json.dumps({'redirectURL':redirectURL})
        
tumblrApp = web.application(urls, locals())
