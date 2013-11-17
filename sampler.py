# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Google+ API.
Usage:
  $ python sampler.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sampler.py --help

"""

import argparse
import httplib2
import os
import sys
import json
import urllib

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

mixedkeys = "mixedkeywords.txt"
# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/1031065614905/apiui>

"""Commented to make the code executeable in emacs interpreter"""
#CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

CLIENT_SECRETS = 'client_secrets.json'
print 'Loaded',CLIENT_SECRETS

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/plus.login',
      'https://www.googleapis.com/auth/plus.me',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv=['']):
  """
  Main method, now defunct, may need to be re-allocated
  """
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Google+ API.
  service = discovery.build('plus', 'v1', http=http)

  try:
    #print activities_document
    return service
    #return getLoads("friends",service)
    #return activities_document 

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

def servGen():
  """
  Generates a 'service' object that handles authentication for
  all API calls in the rest of the code
  """
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)
  print "Credentials authorized"

  # Construct the service object for the interacting with the Google+ API.
  service = discovery.build('plus', 'v1', http=http)
  print "New service generated"
  return service
  
#Code to go over a list of responses and glean images from them
def parse(items):
  """
  The 'post' objects returned by Google can contain many other
  kinds of posts other than photos- for e.g. articles, polls,
  videos etc. This function parses a list of JSON responses
  and prunes out irrelevant types of posts and returns a list
  of only Photo type posts.
  """
  count = 0
  photocount=0
  photolist=[]
  
  for item in items:
    object = item['object']
    if 'attachments' in object:
      attachments = object['attachments']
      for attachment in attachments:
        """Attachment is the base unit where variations happen"""
        if attachment['objectType']=='photo':
          photocount+=1
          print 'photodetected, replies:', object['replies']['totalItems'], ' at elem no.',count
          if 'image' in attachment:
            photolist += [item]
    count+=1
  print "total no. of photos:",photocount
  return photolist

keyfile = "emotion-keywords.txt"

def loadKeys(keyfile):
  """
  Returns a list of keys to perform getLoads on
  """
  f = open(keyfile,'r')
  keylist = []
  for line in f:
    keylist+= [line.strip()]
  return keylist    

def getID(activity):
  """Returns activityID"""
  return activity['id']
  
def getReplies(activityId,service):
  """
  Given an activityId generated from getID, and service
  generated from getServ, this retrieves a JSON response
  from Google containing the comments 
  """
  
  try:
    comments_resource = service.comments()
    comments_doc = comments_resource.list(
      maxResults=200, activityId=activityId).execute()
    return comments_doc
  except Exception as e:
    print "Error occurred", e,type(e)

def getReplynum(activity):
  """
  Gets number of replies for an activity.
  We will use this to judge whether or not to
  make an HTTP call to Google to retrieve comments

  - Don't make an API call to Google if
  getReplynum returns a value of zero
  """
  return activity['object']['replies']['totalItems']

def getPhotoURL(photo):
  """
  Return the URL location of a photo from photolist
  """
  url = photo['object']['attachments'][0]['image']['url']
  return url

def downloadPhoto(url,outfile):
  f = open(outfile,'wb')
  f.write(urllib.urlopen(url).read())
  f.close()
  print "Wrote to ",outfile
  return 
  
def toCommentList(comments_doc):
  """
  Utility function to convert a json response from Google into
  a list of individual comments
  """
  flist = []
  for comment in comments_doc['items']:
    flist = flist + [(comment["object"]["content"],comment["plusoners"]["totalItems"])]
  return flist
  

def getLoads(word, service,limit=100):
  """
  Primary load function for retrieving large amounts of data
  for a particular keyword and then treating it
  New loads function only makes http requests for images with at least one
  comment
  """

  print "Getloads activated:"
  try:
   superlist = []
   activities_resource = service.activities()
   activities_document = activities_resource.search(
       maxResults=20, orderBy ='recent',query=word).execute()
   nextPageToken = activities_document['nextPageToken']
   while (('items' in activities_document)
            and len(activities_document["items"])>0
            and len(superlist)<=limit):
       if 'items' in activities_document:
         print 'Word:',word,'got page with',len(activities_document['items'])

         for activity in activities_document['items']:
           """Photo detection """
           if 'attachments' in activity['object']:
             if activity['object']['attachments'][0]['objectType']=='photo':
               """Ensures at least one response """
               if int(activity['object']['replies']['totalItems'])>0:
                 superlist = superlist + [activity]

       activities_document= activities_resource.search(
         maxResults=20, orderBy='recent',
         query=word,
         pageToken=nextPageToken).execute()
       if 'nextPageToken' in activities_document:
         nextPageToken = activities_document['nextPageToken']
         print "new length is now", len(superlist)
         
   print "Loop ended, limit",len(superlist),"reached"
   return superlist
   
  except Exception as e:
    print "GetLoads Error Encountered", e
    #print dir(e)
    if len(superlist)>0:
      return superlist
    else:
      raise Exception
      return None

def areValidReplies(replies):
  if type(replies)!=dict:
      return False
  if replies == 'NONE':
    return False
  for reply in replies['items']:
    if reply['plusoners']['totalItems']>0:
      return True
  return False 

  
def Driver(keylist):
  photopath = os.getcwd()+"/photos_HL/"
  if not os.path.exists(photopath):
    os.makedirs(photopath)
  #keylist = loadKeys(keyfile)
  try:
    service = servGen()
  except:
    print "Service not generated, program exiting"
    return
  processed = []
  for key in keylist:
    try:
      #response = None
      #while(response==[] and response!=None):
      print "new key",key
      keypath = photopath+key+'/'
      if not os.path.exists(keypath):
        response = getLoads(key,service)
        photos = response
        #photos = parse(response)
        os.makedirs(keypath)
      else:
        continue
      #print key, "response complete", len(response)
      print key,'response received', len(response)
      count = 0
      for photo in photos:
        # Make an API Call only if the number of responses
        # is greater than zero
        """
        Counter will be useful for naming files
        """
        count +=1
        if getReplynum(photo)>0:
          replies = getReplies(getID(photo),service)
        else:
          replies ='NONE'
        if areValidReplies(replies):
          tempjson = [photo,replies]
          url = getPhotoURL(photo)
          try:
            downloadPhoto(url,keypath+str(count)+'cleaned')
            f = open(keypath+str(count)+'cleaned'+'.json','w')
            f.write(json.dumps(tempjson))
            f.close()
          except Exception as e:
            print "Error downloading photo",e
          
      processed += [key]

      
    except Exception as e:
      print "Exception occurred",e
      incomplete= set(keylist)-set(processed)
      return incomplete

  print 'Code Execution complete'
  unfinished = set(keylist)-set(processed)
  return unfinished


#Driver()
# For more information on the Google+ API you can visit:
#
#   https://developers.google.com/+/api/
#
# For more information on the Google+ API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/plus/v1/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
