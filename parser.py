#! /usr/bin/env python
"""
CSS Audit
(C) Kyle Wanamaker, 2011
"""
from sys import argv
from HTMLParser import HTMLParser
import re

import cssutils

script, filename, urlroot = argv

class Cssparser(HTMLParser):
    def __init__(self, fh, urlroot = None):
        HTMLParser.__init__(self)
        self.used_classes = []
        self.defined_classes = []
        self.linked_sheets = []
        self.fileids = []
        self.inline_css_data = []
        self.get_data = False
        self.follow_css_links = True
        self.url_root = urlroot
        self.unchained_classes = []
        
        # this line always goes last
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
        # look for <style type='text/css' ... /> tags usually found in the head
        elif ( tag.lower() == 'style' and 'type' in dattrs and
               dattrs['type'].lower() == 'text/css' ):
            print "Found CSS inline defs"
            self.get_data = True
        self.append_styles(tag, attrs)
    
    def handle_data(self, data):
        if self.get_data == True:
            self.inline_css_data.append(data)
            print self.inline_css_data
            print "Sending to parser"
            self.parse_inline_styles(data, 'string')
            self.get_data = False
        
    def handle_startendtag(self, tag, attrs):
        self.append_styles(tag, attrs)
    
    def append_styles(self, tag, attrs):
        dattrs = dict(attrs)
        if 'class' in dattrs:
            print "Found classes '%s'" % dattrs['class']
            class_string = dattrs['class']
            # These extract the styles without a period, so we have to add 
            # it in.
            r = re.compile('\W+')
            class_names = re.split('\W+', class_string)
            dotted_names = map(prepend_dot, class_names)
            
            self.used_classes.append(' '.join(dotted_names))
            self.unchained_classes.append(dotted_names)

    '''
    Function for parsing styles defined in the body of the document. This only includes data inside of HTML <style> tags, a URL, or file to open.
    '''
    def parse_inline_styles(self, data=None, import_type ='string'):
        if data is None:
            raise
        #parser = cssutils.CSSParser(fetcher=self.replace_handler())
        parser = cssutils.CSSParser()
        if import_type == 'string':
            print "importing string with url=%s" % self.url_root
            sheet = parser.parseString(data,href=self.url_root)
        elif import_type == 'url':
            sheet = parser.parseUrl(data)
        elif import_type == 'file':
            sheet = parser.parseFile(data)
        else:
            raise

        hrefs = []
        for i in range(len(sheet.cssRules)):
            print "loop #%d, TYPE=%d" %  (i, sheet.cssRules[i].type)
            if sheet.cssRules[i].type == cssutils.css.CSSStyleRule.STYLE_RULE:
                selector = sheet.cssRules[i].selectorText
                print "cssparser found  selector: %s" % selector
                self.defined_classes.append(selector)
            elif ( self.follow_css_links == True and
                  sheet.cssRules[i].type == cssutils.css.CSSStyleRule.IMPORT_RULE ):
                href = sheet.cssRules[i].href
                print "Added %s to the stylesheets I'll crawl" % href
                # we'll have to try to add in a url root here, if these are relative
                # links.
                self.linked_sheets.append(self.url_root+href)
                self.parse_inline_styles(data=self.url_root+href, import_type='url')
            else:
                print "You fell through"
                #parse_inline_styles(data=href, import_type='url')
    
    
    def replace_handler(self):
        pass

def prepend_dot(word):
    return '.' + word

if __name__ == '__main__':
    # must send a file to open!
    #f = open('/Users/kyle/src/css-audit/data/yahoo.html', 'r')
    f = open(filename)
    mycssauditor = Cssparser(f, urlroot)
    print "Total classes found %s" % mycssauditor.used_classes
    print "Found these stylesheets %s" % mycssauditor.linked_sheets
    print "Total classes defined: %s" % mycssauditor.defined_classes
    y = mycssauditor.used_classes
    x = mycssauditor.defined_classes
    #unused_classes = [[ x for x if x not in y ]]
    print "Unused classes(maybe)"
    print [ c for c in x if c not in y ]
    print "Used classes without a definition:"
    print [c for c in y if c not in x ]
    #print "Unused defs:  %s" % (unused_classes)

