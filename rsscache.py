#!/usr/bin/env python

import os
import re
import SimpleHTTPServer
import SocketServer
import ssl
import sys
import threading
import time
import urllib2
from hashlib import sha256


def createfolders():
    if not os.path.exists('/www'):
        os.makedirs('/www')

    if not os.path.exists('/www/data'):
        os.makedirs('/www/data')


def startwebserver():
    os.chdir('/www')

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", 8000), Handler)
    print "Serving at port 8000"
    httpd.serve_forever()

def downloadfile(url, filename):
    tries = 1
    while tries <5:
        try:
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.options &= ~ssl.OP_NO_SSLv3
            req = urllib2.Request(url)
            req.add_header(
                'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0')
            remotefile = urllib2.urlopen(req, context=ctx)
            with open(filename, 'wb') as output:
                output.write(remotefile.read())
            break
        except Exception as e:
            tries += 1
            print 'Error when downloading the file [{0}]\n{1}'.format(tries,str(e))
            time.sleep(3000)

def getlinksfromfile(filename):
    with open(filename, 'r') as input:
        buffer = input.read()
        regex = r"(\>|\"|\')(?P<url>https?:\/\/.*?(?P<ext>\.jpg|\.jpeg|\.png).*?)(\<|\"|\')"
        matches = re.finditer(regex, buffer, re.MULTILINE)

        for match in matches:
            addfileurl = match.group('url')
            addfilelocal = '/data/' + \
                sha256(addfileurl).hexdigest() + match.group('ext')
            if os.path.isfile('/www' + addfilelocal):
                print '{0} found skipping'.format(addfileurl)
            else:
                print '{0} downloading --> {1}'.format(
                    addfileurl, addfilelocal)
                downloadfile(addfileurl, '/www' + addfilelocal)
            buffer = buffer.replace(addfileurl,host_name + addfilelocal)

        with open(filename,'wb') as output:
            output.write(buffer)

def run():
    while True:
        for feed in feeds:
            print ('{0} processing...'.format(feed[0]))
            downloadfile(feed[0], '/www/' + feed[1])
            getlinksfromfile('/www/' + feed[1])

        print 'sleeping for 15 min'
        time.sleep(15 * 60)

def startdownloadserver():
    thread = threading.Thread(target = run)
    thread.daemon = True
    thread.start()

host_name = os.environ['host_name']
feeds = [(feed.split('|')[0],feed.split('|')[1]) for feed in os.environ['feeds'].split(';')]

for feed in feeds:
    print 'Feed URL {0} --> {1}/{2}'.format(feed[0],host_name,feed[1])

createfolders()
startdownloadserver()
startwebserver()
