import findLibs
import wordspew

import web
from web import form

import json


urls = (
"", "WordSpewInterface",
)

render = web.template.render('templates/')

class WordSpewInterface:
  def GET(self):
    params = web.input()
    numParams = len(params.keys())
    if "getspew" in params.keys():
      numspew = 1
      if "num" in params.keys():
        numspew = int(params["num"])
      ret = []
      for i in range (0, numspew):
        ret.append (wordspew.getPhrase())
      return json.dumps(ret)
    
  def POST(self):
    return json.dumps(None)

wordspewApp = web.application(urls, locals())
