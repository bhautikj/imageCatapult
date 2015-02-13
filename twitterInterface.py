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
import twitter

# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

class TwitterObject(OAuthObjectBase):
  def __init__(self):
    OAuthObjectBase.__init__(self)
    self.apiName = "twitter"

  def authPart1(self):
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer             = oauth.Consumer(key=self.api_key, secret=self.api_secret)
    oauth_client               = oauth.Client(oauth_consumer)

    resp, content = oauth_client.request(twitter.REQUEST_TOKEN_URL, 'GET')    
    request_token = dict(parse_qsl(content))

    auth_url =  '%s?oauth_token=%s' % (twitter.AUTHORIZATION_URL, request_token['oauth_token'])

    self.oauth_token = request_token['oauth_token']
    self.oauth_token_secret = request_token['oauth_token_secret']
    
    return auth_url

  def authPart2(self, oauth_token, oauth_verifier):
    token = oauth.Token(self.oauth_token, self.oauth_token_secret)
    token.set_verifier(oauth_verifier)

    oauth_consumer             = oauth.Consumer(key=self.api_key, secret=self.api_secret)
    
    oauth_client  = oauth.Client(oauth_consumer, token)
    resp, content = oauth_client.request(twitter.ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % oauth_verifier)
    access_token  = dict(parse_qsl(content))
    
    self.final_oauth_token = access_token['oauth_token']
    self.final_oauth_token_secret = access_token['oauth_token_secret']

    authDict = authPickler.getAuthDict(self.apiName)
    authDict["final_oauth_token"] = self.final_oauth_token
    authDict["final_oauth_token_secret"] = self.final_oauth_token_secret
    authPickler.setAuthDict(self.apiName, authDict)
    self.authorised = True

    self.setupAPI()

    return redirectToUrlText(web.ctx.homedomain)

  def setupAPI(self):
    self.twitter = twitter.Api(consumer_key=self.api_key,
                            consumer_secret=self.api_secret,
                            access_token_key=self.final_oauth_token,
                            access_token_secret=self.final_oauth_token_secret) 
    
  def postImagePost(self, jobDict):
    textToPost = str(jobDict["title"]) + " " + str(jobDict["flickrshorturl"])
    self.twitter.PostUpdate(textToPost)

  def postTestPost(self):
    self.twitter.PostUpdate("TEST")
    
#-------------------------------------------------------------------------------

urls = (
"", "TwitterAuth",
)

appForm = form.Form(
  form.Textbox('Twitter API Key', form.notnull),
  form.Password('Twitter API Secret', form.notnull),
)

render = web.template.render('templates/')

twitterObject = TwitterObject()
twitterObject.setup()

class TwitterAuth:
  def GET(self, path=None):
    global twitterObject

    if not twitterObject.authorised:
      params  = web.input()
      if 'oauth_token' in params.keys() and 'oauth_verifier' in params.keys():
        return twitterObject.authPart2(params['oauth_token'], params['oauth_verifier'])

  def POST(self):
    params = web.input()
    global twitterObject
    if "submitInitial" in params.keys():
      apiKey = params["apiKey"]
      apiSecret = params["apiSecret"]
      
      twitterObject.setupApp(apiKey, apiSecret)
      redirectURL =  twitterObject.authPart1()

      return json.dumps({'redirectURL':redirectURL})

    
twitterApp = web.application(urls, locals())
