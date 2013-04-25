import findLibs
from imagedb import imagedb

import web
from web import form

import json


urls = (
"", "TemplateInterface",
)

render = web.template.render('templates/')

class TemplateInterface:
  def GET(self):
    params = web.input()
    numParams = len(params.keys())
    
    if "saveTemplate" in params.keys():
      name = params["saveTemplate"]
      templateDict = json.dumps(params)
      imagedb.addTemplate(name, templateDict)
    elif "templateList" in params.keys():
      tmps = imagedb.getAllTemplateNames()
      ret = {}
      if tmps != None:
        for tmp in tmps:
          ret[str(tmp[0])] = str(tmp[1])
      print "returning template list", ret
      return json.dumps(ret)
    elif "getTemplate" in params.keys():
      ret = imagedb.getTemplate(params["getTemplate"])
      if ret == None:
        return json.dumps(None)
      return ret[0][0]
    
    return json.dumps(None)
    
  def POST(self):
    return json.dumps(None)

templateApp= web.application(urls, locals())
