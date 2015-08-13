
import psycopg2
import urllib
import urllib2
import subprocess
import urlparse
import lxml.html
import json
import sys

try:
    ACCESS_TOKEN = sys.argv[1]
except:
    print "No access token, trying alternative method"
    FACEBOOK_APP_ID     = '786801594764538'
    FACEBOOK_APP_SECRET = '8f3e01802310a45f45b8182364eaf036'


    # Trying to get an access token. Very awkward.
    oauth_args = dict(client_id     = FACEBOOK_APP_ID,
                      client_secret = FACEBOOK_APP_SECRET,
                      grant_type    = 'client_credentials')
    oauth_curl_cmd = ['curl',
                      'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
    print oauth_curl_cmd
    oauth_response = subprocess.Popen(oauth_curl_cmd,
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE).communicate()[0]

    try:
        print urlparse.parse_qs(str(oauth_response))
    except KeyError:
        print('Unable to grab an access token!')
        exit()

try:
    conn = psycopg2.connect("dbname='itsdev' host='localhost'")
    cur = conn.cursor()
except:
    print "I am unable to connect to the database"

doc = lxml.html.fromstring(urllib2.urlopen("http://govsm.com/w/House").read())
for fb_links in doc.xpath("//a[contains(@href, 'facebook')]"):
    fb_url = fb_links.attrib['href']
    username = fb_url[fb_url.find('.com')+5:]
    print "Looking for username: " + username
    try:
        metadata = json.loads(urllib2.urlopen('https://graph.facebook.com/'+username+'?access_token=%s'%ACCESS_TOKEN).read())
        _id = metadata['id']
        name = metadata['name']
    except:
        print 'could not find legislator id %s' % username
        continue

    cur.execute("select exists(select 1 from legislator where fb_id='%s');" % _id)
    if not cur.fetchone()[0]:
        insert_st = "INSERT INTO legislator VALUES (%s,%s,%s)"
        cur.execute(insert_st, ('Unknown', _id, name))

    try:
        fb_leg_obj = json.loads(urllib2.urlopen('https://graph.facebook.com/'+username+'?fields=statuses&access_token=%s'%ACCESS_TOKEN).read())
        print "Accessed: " + 'https://graph.facebook.com/'+username+'?fields=statuses&access_token=%s'%ACCESS_TOKEN
    except:
        print 'could not get fb page'
        continue
    for data in fb_leg_obj['statuses']['data']:
        insert_st = 'INSERT INTO status VALUES (%s, %s, %s)'
        cur.execute("select exists(select 1 from status where status_id='%s');" % data['id'])
        if not data.get('message'):
            continue
        if not cur.fetchone()[0]:
            cur.execute(insert_st, (data['from']['id'], data['message'], data['id']))

    print "============================================="

conn.commit()
cur.close()
conn.close()

