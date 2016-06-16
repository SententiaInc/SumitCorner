
# coding: utf-8

# In[1]:

import urllib2
import json
import datetime
import csv
import time
import sys


# In[6]:

app_id = "1106900905999971"
app_secret = "399f3d64319058085e3fa76414ff240e"

access_token = app_id + "|" + app_secret


# In[7]:

page_id = 'statefarm'


# In[8]:

# Needed to write tricky unicode correctly to csv; not present in tutorial
def unicode_normalize(text):
	return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22, 0xa0:0x20 }).encode('utf-8')


# def testFacebookPageData(page_id, access_token):
#     
#     # construct the URL string
#     base = "https://graph.facebook.com/v2.6"
#     node = "/" + page_id + "/posts"
#     parameters = "/?limit=1&access_token=%s" % access_token
#     url = base + node + parameters
#     
#     # retrieve data
#     req = urllib2.Request(url)
#     response = urllib2.urlopen(req)
#     data = json.loads(response.read())
#     
#     print json.dumps(data, indent=4, sort_keys=True)
#     
# 
# testFacebookPageData(page_id, access_token)

# In[17]:

def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print e
            time.sleep(5)
            
            print "Error for URL %s: %s" % (url, datetime.datetime.now())

    return response.read()


# def testFacebookPageFeedData(page_id, access_token):
#     
#     # construct the URL string
#     base = "https://graph.facebook.com/v2.4"
#     node = "/" + page_id + "/posts" # changed
#     parameters = "/?access_token=%s" % access_token
#     url = base + node + parameters
#     
#     # retrieve data
#     data = json.loads(request_until_succeed(url))
#     
#     print json.dumps(data, indent=4, sort_keys=True)
#     
# 
# testFacebookPageFeedData(page_id, access_token)

# In[18]:

def getFacebookPageFeedData(page_id, access_token, num_statuses):
    
    # construct the URL string
    base = "https://graph.facebook.com/v2.6"
    node = "/" + page_id + "/posts" 
    parameters = "/?fields=message,link,created_time,type,name,id,comments.limit(1).summary(true),shares,reactions.limit(1).summary(true)&limit=%s&access_token=%s" % (num_statuses, access_token) # changed
    url = base + node + parameters
    
    # retrieve data
    data = json.loads(request_until_succeed(url))
    
    return data
    

## test_status = getFacebookPageFeedData(page_id, access_token, 1)["data"][0]
## print json.dumps(test_status, indent=4, sort_keys=True)


# In[22]:

def processFacebookPageFeedStatus(status):
    
    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.
    
    # Additionally, some items may not always exist,
    # so must check for existence first
    
    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else unicode_normalize(status['message'])
    link_name = '' if 'name' not in status.keys() else unicode_normalize(status['name'])
    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else unicode_normalize(status['link'])
    
    
    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.
    
    status_published = datetime.datetime.strptime(status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=-5) # EST
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S') # best time format for spreadsheet programs
    
    # Nested items require chaining dictionary keys.
    
    num_reactions = status.get('reactions', {}).get('summary', {}).get('total_count', None)
    num_comments = status.get('comments', {}).get('summary', {}).get('total_count', None)
    num_shares = status.get('shares', {}).get('count', None)
    
    #num_reactions = 0 if 'reactions' not in status.keys() else status['reactions']['summary']['total_count']
    #num_comments = 0 if 'comments' not in status.keys() else status['comments']['summary']['total_count']
    #num_shares = 0 if 'shares' not in status.keys() else status['shares']['count']
    
    # return a tuple of all processed data
    return (status_id, status_message, link_name, status_type, status_link,
           status_published, num_reactions, num_comments, num_shares)


## processed_test_status = processFacebookPageFeedStatus(test_status)
## print processed_test_status


# In[24]:

def scrapeFacebookPageFeedStatus(page_id, access_token):
    with open('%s_facebook_statuses.csv' % page_id, 'wb') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "link_name", "status_type", "status_link",
           "status_published", "num_reactions", "num_comments", "num_shares"])
        
        has_next_page = True
        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()
        
        print "Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime)
        
        statuses = getFacebookPageFeedData(page_id, access_token, 100)
        
        while has_next_page:
            for status in statuses['data']:
                w.writerow(processFacebookPageFeedStatus(status))
                
                # output progress occasionally to make sure code is not stalling
                num_processed += 1
                if num_processed % 1000 == 0:
                    print "%s Statuses Processed: %s" % (num_processed, datetime.datetime.now())
					
            # if there is no next page, we're done.
            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(statuses['paging']['next']))
            else:
                has_next_page = False
                
        
        print "\nDone!\n%s Statuses Processed in %s" % (num_processed, datetime.datetime.now() - scrape_starttime)


# In[25]:

if __name__ == '__main__':
	
	page_id = sys.argv[1]
	scrapeFacebookPageFeedStatus(page_id, access_token)


# In[ ]:



