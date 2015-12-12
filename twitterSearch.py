from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import json
import urllib, urllib2
from locale import getlocale
import tweepy
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
# get geolocation from a named location:
# def getLocRequest():
#     location = raw_input('Enter your location/desired location: ')
#     key = 'AIzaSyDBh1sqfIh7C0ewUJOG3kbSz4yxRx48Q3E'
#     params = {'address' : location, 'key' : key}
#     baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?'
#     requestLocURL = baseurl + urllib.urlencode(params)
# #     print requestLocURL
#     response = safeGet(requestLocURL)
#     if response is not None:
#         return json.loads(response.read())
#     else:
#         return None

# Returns a dictionary of the name, latitude and longitude of a particular place. 
# def processGeoCodeData(data): #accepts the results portion
#     if data['status'] == 'OK':
#         name = data['results'][0]['formatted_address']
#         lat = data['results'][0]['geometry']['location']['lat']
#         long = data['results'][0]['geometry']['location']['lng']
#         return {'name' : name, 'lat' : lat, 'long' : long}
#     else:
#         return data['status']

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print "The server couldn't fulfill the request." 
        print "Error code: ", e.code
    except urllib2.URLError, e:
        print "We failed to reach a server"
        print "Reason: ", e.reason
    return None

# Searches tweets using the Tweepy API. 
def searchTweets(api, queryA, queryB):
#     latlongDict = processGeoCodeData(getLocRequest())
#     lat = latlongDict['lat']
#     long = latlongDict['long']
#     geostr = str(lat) + "," + str(long) + "," + "5mi" 
    cursorA = tweepy.Cursor(api.search, q=queryA, count=10)
    tweetListA = [tweet.text for page in cursorA.pages(10) for tweet in page]
    cursorB = tweepy.Cursor(api.search, q=queryB, count=10)
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

tweetLists = searchTweets(api, "samsung", "apple")
requestString = formatRequest(tweetLists[0])
jsonDict = querySentimentAnalysis(requestString)
avgPolarityA = analyzeTweets(jsonDict)

requestString = formatRequest(tweetLists[1])
jsonDict = querySentimentAnalysis(requestString)
avgPolarityB = analyzeTweets(jsonDict)
print avgPolarityA
print avgPolarityB
    