#!/usr/bin/env python

import sys
import random
import argparse
import urllib2
import lxml.html


PROXIES = 'proxies'
AGENTS = 'agents'

RETRY=5
def random_line(from_file):
    with open(from_file) as infile:
        cleaned = (line for line in infile if line.strip() and not line.startswith('#'))
        line = next(cleaned)
        for num, aline in enumerate(infile):
            if random.randrange(num + 2):
                continue
            line = aline
        return line.strip()


def get_markup(url, tries = 0):
    agent = random_line(AGENTS)
    headers = [('User-Agent', agent)]
    proxy = random_line(PROXIES).split(',')

    #print "Proxy: " + str(proxy)
    #print "Agent: " + str(agent)

    if proxy:
        proxy_support = urllib2.ProxyHandler({proxy[0]: proxy[1]})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        opener.addheaders = headers
    else:
        opener = urllib2.build_opener()
        opener.addheaders = headers
    try:
        f = opener.open(url)
        return f.read()
    except (IOError, ValueError, TypeError), err:
        print url.strip() + " " + str(err).encode('UTF-8')
        if tries<=RETRY:
            tries+=1
            print " ... trying ["+str(tries)+"]"
            return get_markup(url, tries)
    return False


def main(url):
    root = lxml.html.fromstring(get_markup(url))
    spans = [span.text for span in root.cssselect('.servers_launched span')
            if span.text.isdigit()]
    print "Current droplet count: " + "".join(spans)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get DO droplet count.')
    parser.add_argument("-u", dest='url', default='https://www.digitalocean.com/')
    args = parser.parse_args()
    main(args.url)
