#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import logging
import json
import jinja2
import webapp2, urllib2, os, urllib
import sys


sys.path.append(os.path.join(os.path.dirname(__file__)+"/lib/python2.7/site-packages"))
logging.info(sys.path)
import tweepy


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values={}
        template_values["page_title"] = "Which Is Better?"
        logging.info("In MainHandler")
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
class SentimentResponseHandler(webapp2.RequestHandler):
    def post(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        
        vals = {}
        vals["page_title"] = "Results"
        thingA = self.request.get('thingA')
        thingB = self.request.get('thingB')
        go = self.request.get('gobtn')
        vals["thingA"] = thingA.title()
        vals["thingB"] = thingB.title()
        logging.info(thingA)
        logging.info(thingB)
        logging.info(go)

        
        tweetLists = searchTweets(api, thingA, thingB)
        requestString = formatRequest(tweetLists[0])
        jsonDict = querySentimentAnalysis(requestString)
        avgPolarityA = analyzeTweets(jsonDict)

        requestString = formatRequest(tweetLists[1])
        jsonDict = querySentimentAnalysis(requestString)
        avgPolarityB = analyzeTweets(jsonDict)
        diffpercentage = compareValue(avgPolarityA, avgPolarityB)
        
        
        vals["feelingA"] = "{0:.2f}".format(avgPolarityA)
        vals["feelingB"] = "{0:.2f}".format(avgPolarityB)
        if (avgPolarityA > avgPolarityB):
            vals["aGreaterb"] = 1
        elif (avgPolarityB > avgPolarityA):
            vals["aGreaterb"] = 0
        else:
            vals["aGreaterb"] = 2
            
        vals["percentage"] = "{0:.1f}".format(diffpercentage)
        template = JINJA_ENVIRONMENT.get_template('displayResults.html')
        self.response.write(template.render(vals))
        
application = webapp2.WSGIApplication([ \
                                      ('/sResponse', SentimentResponseHandler),
                                      ('/.*', MainHandler),
                                      ('/index', MainHandler)
                                      ],
                                     debug=True)




# APPLICATION BACK-END CODE:
# Searches tweets using the Tweepy API. 
def searchTweets(api, queryA, queryB):
#     latlongDict = processGeoCodeData(getLocRequest())
#     lat = latlongDict['lat']
#     long = latlongDict['long']
#     geostr = str(lat) + "," + str(long) + "," + "5mi" 
    cursorA = tweepy.Cursor(api.search, q=queryA, count=100)
    tweetListA = [tweet.text for page in cursorA.pages(10) for tweet in page]
    cursorB = tweepy.Cursor(api.search, q=queryB, count=100)
    tweetListB = [tweet.text for page in cursorB.pages(10) for tweet in page]
    print len(tweetListA)
    print len(tweetListB)
    return [tweetListA, tweetListB]

# Takes the list of tweets, builds a request matching the Sentiment140 Format.
# Returns a formatted request string. 
def formatRequest(tweetList):
    url = "http://www.sentiment140.com/api/bulkClassifyJson?"
    encodeID = urllib.urlencode({"appid":"zzchua@uw.edu"})
    dataDict = {"language": "auto", "data": []}
    for tweet in tweetList:
        dataDict["data"].append({"text":tweet})
    jsonDict = json.dumps(dataDict)
    print jsonDict
    requestURL = url + encodeID
    print requestURL
    req = urllib2.Request(requestURL, jsonDict)
    #print req
    return req

# Accepts a url request string and queries Sentiment140.
# Returns a json dictionary with polarity.
def querySentimentAnalysis(request):
    response = urllib2.urlopen(request)
    print response
    responseString = response.read()
    print responseString
    responseString = unicode(responseString,'latin-1')
    jsonDict = json.loads(responseString)
    print jsonDict
    return jsonDict

def analyzeTweets(dataDict):
    # 0, 2, 4. 
    numTweets = len(dataDict["data"])
    listPolarity = [tweet["polarity"] for tweet in dataDict["data"]]
    totalPolarity = 0
    for polarity in listPolarity:
        totalPolarity = totalPolarity + polarity
    avgPolarity = float(totalPolarity)/numTweets
    return avgPolarity

def compareValue(polA, polB):
    if polA > polB:
        diff = polA - polB
        percentage = diff/polB * 100.0
    elif polB > polA:
        diff = polB - polA
        percentage = diff/polA * 100.0        
    else:
        percentage = 0.0
    return percentage
        
    
    
    
    
    
    