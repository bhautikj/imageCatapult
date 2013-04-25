import sys
pathList = ['lib']

for path in pathList:
  if path not in sys.path:
    sys.path.append(path)
