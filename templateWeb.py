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
