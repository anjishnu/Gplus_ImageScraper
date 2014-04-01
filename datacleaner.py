import sampler, json, os
"""
The goal of this module is to prune already loaded data to the standards required
for the project.
"""

print "Pruner Loaded"

photopath = os.getcwd()+"/photos_HL/"
photopath1 = os.getcwd()+"/photos/"

def datagleaner(rootpath=photopath1):
  for path, subdirs, files in os.walk(rootpath):
    for name in files:
      if '.json' in name:
        curpath = os.path.join(path,name)
        f = open(curpath,'r+')
        try:
          json_obj = json.load(f)
        except:
          json_obj = ["None"]
        return json_obj
        
def datacleaner(rootpath=photopath1):
  removedlist = []
  for path, subdirs, files in os.walk(rootpath):
    for name in files:
     if '.json' in name:
        print name
        curpath = os.path.join(path, name)
        #print "Current path",curpath
        f = open(curpath,'r+')
        try:
          ob_json = json.load(f)
        except:
          ob_json = ["NONE","NONE"]
        #print "JSON successfully loaded"
        f.close()
        replies = ob_json[1]
        #print "Replies Successfully loaded"
        #Check to see if the replies contained in the
        try:
         if not sampler.areValidReplies(replies):
            ###Delete both the json file and the associated image
            print "Current path", curpath
            print "Invalid file detected at",name
            photoname = name.split('.')[0]
            os.remove(curpath)
            print "Deleted", curpath
            photo_location = os.path.join(path,photoname) 
            os.remove(photo_location)
            print "Deleted", photo_location
            removedlist += [(photoname,path)]
         else:
           #File is good already
           if 'cleaned' not in name:
             name = name.split(".")
             newname = name[0]+'cleaned.json'
             os.rename(curpath,os.path.join(path,newname))
             photo_location = os.path.join(path,photoname) 
             os.rename(photo_location,photo_location+'cleaned')
            
        except Exception as e:
            print type(e)
            print curpath
            raise e

  print "Data Clean Completed"
  return removedlist
           