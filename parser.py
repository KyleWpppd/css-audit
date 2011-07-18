"""
CSS Audit
(C) Kyle Wanamaker, 2011
"""

from HTMLParser import HTMLParser

class cssaudit(HTMLParser):
    def __init__(self, fh):
        HTMLParser.__init__(self)
        self.fileids = []
        self.feed(fh.read())

    def handle_starttag(self, tag, attrs):
        print attrs


