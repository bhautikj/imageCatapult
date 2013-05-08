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
import paths

import os
import pickle

picklePath = os.path.join(paths.appBase, "auth.pickle")
def getAuthDict(service):
  try:
    dict = pickle.load(open(picklePath,"rb"))
    if service == None:
      return dict
    if service in dict.keys():
      return dict[service]
    else:
      return {}
  except:  
    return {} 

def setAuthDict(service, authDict):
  dict = getAuthDict(None)
  dict[service] = authDict
  return pickle.dump(dict, open(picklePath,"wb"))

def availableServices():
  dict = getAuthDict(None)
  return dict.keys()