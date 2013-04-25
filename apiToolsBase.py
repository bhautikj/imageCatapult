import findLibs
import authPickler

def redirectToUrlText(url):
  text = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <html>
    <head>
    <title>Your Page Title</title>
    <meta http-equiv="REFRESH" content="0;url=''' + url +  '''"></HEAD>
    <BODY>
    Redirecting, click <a href="''' + url + '''">here</a> if not redirected immediately.
    </BODY>
    </HTML>
    '''
  return text

class OAuthObjectBase:
  def __init__(self):
    self.hasApp = False
    self.api_key = ""
    self.api_secret = ""
    #temporary vars needed for two-part authorisation
    self.oauth_token = ""
    self.oauth_token_secret = ""
    #these are used to create the flickrAPI object
    self.final_oauth_token = ""
    self.final_oauth_token_secret = ""
    #if we have been authorised
    self.authorised = False
    self.apiName = "THIS_NEEDS_TO_BE_OVERRIDDEN"

  def setup(self):
    #attempt to get API keys
    self.attemptGetAPIAuth()

    #attempt to authorise
    self.attemptReadAuth()

  def attemptGetAPIAuth(self):
    print "initialising: " + self.apiName
    authDict = authPickler.getAuthDict(self.apiName)
    if "api_key" in authDict.keys() and \
        "api_secret" in authDict.keys():
      self.api_key = authDict["api_key"]
      self.api_secret = authDict["api_secret"]
      self.hasApp = True
      if "publishURL" in authDict.keys():
        self.publishURL =  authDict["publishURL"]

  def attemptReadAuth(self):
    authDict = authPickler.getAuthDict(self.apiName)
    if "final_oauth_token" in authDict.keys():
      self.final_oauth_token = authDict["final_oauth_token"]
      if "final_oauth_token_secret" in authDict.keys():
        self.final_oauth_token_secret = authDict["final_oauth_token_secret"]
      self.authorised = True
      self.setupAPI()

  def setupApp(self, api_key, api_secret, publishURL=None):
    authDict = authPickler.getAuthDict(self.apiName)
    authDict["api_key"] = api_key
    authDict["api_secret"] = api_secret
    if publishURL != None:
      authDict["publishURL"] = publishURL
    authPickler.setAuthDict(self.apiName, authDict)
    self.api_key = authDict["api_key"]
    
    self.api_secret = authDict["api_secret"]
    if publishURL != None:
      self.publishURL = authDict["publishURL"] 
    self.hasApp = True
    return True