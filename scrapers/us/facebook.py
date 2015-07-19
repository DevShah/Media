
import psycopg2

import urllib2
import lxml.html
import json
import sys

try:
    ACCESS_TOKEN = sys.argv[1]
except:
    print "No access token"
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



conn.commit()
cur.close()
conn.close()

