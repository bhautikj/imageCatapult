import findLibs
import authPickler
from apiToolsBase import OAuthObjectBase
from apiToolsBase import redirectToUrlText

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

    return redirectToUrlText(auth_url)

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

    return redirectToUrlText(web.ctx.homedomain + "/auth")

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

appForm = form.Form(
  form.Textbox('Tumblr blog URL', form.notnull),
  form.Textbox('Tumblr API Key', form.notnull),
  form.Password('Tumblr API Secret', form.notnull),
)

render = web.template.render('templates/')

tumblrObject = TumblrObject()
tumblrObject.setup()

class TumblrAuth:
  def GET(self, path=None):
    global tumblrObject

    if not tumblrObject.hasApp:
      form = appForm()
      return render.getTumblrApp(form)

    if not tumblrObject.authorised:
      params  = web.input()
      if 'oauth_verifier' in params.keys():
        return tumblrObject.authPart2(params['oauth_verifier'])
      else:
        return tumblrObject.authPart1()
    else:
      return "Error: Tumblr already authorised!"

  def POST(self):
    form = appForm()
    if not form.validates():
      return render.getTumblrApp(form)
    else:
      if not tumblrObject.setupApp(form['Tumblr API Key'].value, form['Tumblr API Secret'].value, form['Tumblr blog URL'].value):
        return render.getTumblrApp(form)
      else:
        return redirectToUrlText(web.ctx.homedomain + "/tumblrAuth?")
    
tumblrApp = web.application(urls, locals())
