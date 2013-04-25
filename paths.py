import os

from os.path import expanduser

def createDir(dirname):
  try:
    os.makedirs(dirname)
  except:
    pass
  
home = expanduser("~")
appBase = os.path.join(home, ".pyButler")
#imageStore
imageBase = os.path.join(appBase,"imagestore")

createDir(appBase)
createDir(imageBase)

displayBase = ("imagestore")