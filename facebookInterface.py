import findLibs
import authPickler
from apiToolsBase import OAuthObjectBase
from apiToolsBase import redirectToUrlText

import urllib2
import urlparse

import web
from web import form

import facebook

class FacebookObject(OAuthObjectBase):
  def __init__(self):
    OAuthObjectBase.__init__(self)
    self.apiName = "facebook"

  def authPart1(self):
    auth_url = 'https://www.facebook.com/dialog/oauth?client_id=' + self.api_key + \
               '&redirect_uri=' + web.ctx.homedomain + '/facebookAuth&scope=offline_access,publish_stream'
    return redirectToUrlText(auth_url)

  def authPart2(self, code):
    access_token_url = 'https://graph.facebook.com/oauth/access_token?client_id=' + self.api_key + \
                       '&redirect_uri=' + web.ctx.homedomain + '/facebookAuth' + \
                       '&client_secret=' + self.api_secret + '&code=' + code

    pageGet = urllib2.urlopen(access_token_url).read()
    self.final_oauth_token = urlparse.parse_qs(pageGet)['access_token'][0]
    authDict = authPickler.getAuthDict(self.apiName)
    authDict["final_oauth_token"] = self.final_oauth_token
    authPickler.setAuthDict(self.apiName, authDict)
    self.authorised = True

    self.setupAPI()
    
    return redirectToUrlText(web.ctx.homedomain + "/auth")

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

appForm = form.Form(
  form.Textbox('Facebook API Key', form.notnull),
  form.Password('Facebook API Secret', form.notnull),
)

render = web.template.render('templates/')

facebookObject = FacebookObject()
facebookObject.setup()

class FacebookAuth:
  def GET(self, path=None):
    global facebookObject

    if not facebookObject.hasApp:
      form = appForm()
      return render.getFacebookApp(form)

    if not facebookObject.authorised:
      params  = web.input()
      if 'code' in params.keys():
        return facebookObject.authPart2(params['code'])
      else:
        return facebookObject.authPart1()
    else:
      return "Error: Facebook already authorised!"

  def POST(self):
    form = appForm()
    if not form.validates():
      return render.getFacebookApp(form)
    else:
      if not facebookObject.setupApp(form['Facebook API Key'].value, form['Facebook API Secret'].value):
        return render.getFacebookApp(form)
      else:
        return redirectToUrlText(web.ctx.homedomain + "/facebookAuth?")

facebookApp = web.application(urls, locals())
