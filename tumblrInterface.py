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
