"""
CSS Audit
(C) Kyle Wanamaker, 2011
"""

from HTMLParser import HTMLParser

class Cssparser(HTMLParser):
    def __init__(self, fh):
        HTMLParser.__init__(self)
        self.css_classes = []
        self.fileids = []
        self.feed(fh.read())

    
    def handle_starttag(self, tag, attrs):
        self.append_styles(tag, attrs)
    
    def handle_startendtag(self, tag, attrs):
        self.append_styles(tag, attrs)
    
    def append_styles(self, tag, attrs):
        dattrs = dict(attrs)
        if 'class' in dattrs:
            print "Found classes '%s'" % dattrs['class']
            self.css_classes.append(dattrs['class'])



# must send a file to open!
f = open('/Users/kyle/src/css-audit/data/yahoo.html', 'r')
mycssauditor = Cssparser(f)
print "Total classes found %s" % mycssauditor.css_classes


