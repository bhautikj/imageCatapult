import findLibs
import newsHAL

import web
from web import form

import json


urls = (
"", "NewsHALInterface",
)

render = web.template.render('templates/')

class NewsHALInterface:
  def GET(self):
    params = web.input()
    numParams = len(params.keys())
    reply = ""
    try:
      reply = newsHAL.newshal.get_reply_nolearn("")
      print reply
    except:
      print "ARG"
      pass
    return reply
    
  def POST(self):
    return json.dumps(None)

newsHALApp = web.application(urls, locals())
