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
