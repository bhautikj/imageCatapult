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