#https://dev.twitter.com/apps/new

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
    textToPost = jobDict["title"] + " " + jobDict["flickrshorturl"]
    self.twitter.PostUpdate(textToPost)
    
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
