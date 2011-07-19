"""
CSS Audit
(C) Kyle Wanamaker, 2011
"""
from sys import argv
from HTMLParser import HTMLParser

script, filename = argv

class Cssparser(HTMLParser):
    def __init__(self, fh):
        HTMLParser.__init__(self)
        self.used_classes = []
        self.defined_classes = []
        self.linked_sheets = []
        self.fileids = []
        self.get_data = False
        self.feed(fh.read())


    
    def handle_starttag(self, tag, attrs):
        dattrs = dict(attrs)
        
        # look for '<link type='text/css' rel='stylesheet' href='...' /> tags
        if tag.lower() == 'link':
            if all (k in dattrs for k in ('rel', 'href', 'type')):
                if ( dattrs['rel'].lower() == 'stylesheet' and 
                     dattrs['type'].lower == 'text/css' ):
                    #try to open the url...
                    self.linked_sheets.append(dattrs['href'])
        elif ( tag.lower() == 'style' and 'type' in dattrs and
                  dattrs['type'].lower() == 'text/css' ):
            print "Found CSS inline defs"
            self.get_data = True
            print '====='
            
            
        self.append_styles(tag, attrs)
    
    def handle_data(self, data):
        if self.get_data == True:
            self.inline_css_data = data
            print self.inline_css_data
            self.get_data = False
        
    def handle_startendtag(self, tag, attrs):
        self.append_styles(tag, attrs)
    
    def append_styles(self, tag, attrs):
        dattrs = dict(attrs)
        if 'class' in dattrs:
            print "Found classes '%s'" % dattrs['class']
            self.used_classes.append(dattrs['class'])



if __name__ == '__main__':
    # must send a file to open!
    #f = open('/Users/kyle/src/css-audit/data/yahoo.html', 'r')
    f = open(filename)
    mycssauditor = Cssparser(f)
    print "Total classes found %s" % mycssauditor.used_classes
    print "Found these stylesheets %s" % mycssauditor.linked_sheets
    


