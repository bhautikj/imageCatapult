import findLibs
from imagedb import imagedb

import web
from web import form

import json


urls = (
"", "TagsInteraface",
)

render = web.template.render('templates/')

class TagsInteraface:
  def GET(self):
    params = web.input()
    numParams = len(params.keys())
    if "searchTags" in params.keys():
      searchString = params["searchTags"]
      resultRaw = imagedb.searchTags(searchString)
      toReturn = []
      if resultRaw != None:
        for r in resultRaw:
          toReturn.append(r[0])
     
      return json.dumps({"results":toReturn})
    
  def POST(self):
    return json.dumps(None)

tagsApp= web.application(urls, locals())
