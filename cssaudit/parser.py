#! /usr/bin/env python
"""
CSS Audit
(C) Kyle Wanamaker, 2011
Licensed under the GNU General Public License version 3
Please see: http://www.gnu.org/licenses/ for the text of
the GPL v3. 

A copy of the GNU GPL v3 is included with the PyPi package
"""
from sys import argv, exit
from HTMLParser import HTMLParser
import re
import urllib2

import cssutils


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
        self.used_ids = []
        self.used_elements = []
        # this line always goes last
        self.feed(fh.read())
        print "Linked sheets %s " % self.linked_sheets
        for sheet in self.linked_sheets:
            print "And the sheet is %s" % sheet,
            print "Because linked_sheets is: %s " % self.linked_sheets
            self.parse_inline_styles(sheet, 'url')

    
    def handle_starttag(self, tag, attrs):
        """
        This method handles any HTML tags that have a matching
        closing tag. So elements like <p> and <div> are handled 
        by this method.
        @param <string> tag
           An html tag that has a separate closing tag such as <p>
           <div> or <body>
        @param <tuple> attrs
           A tuple of HTML element attributes such as 'class', 'id',
           'style', etc. The tuple is of the form ('html_attribute',
           'attr1', 'attr2', 'attr3' ... 'attrN')
        """
        dattrs = dict(attrs)
        # look for '<link type='text/css' rel='stylesheet' href='...' > tags
        # to see if looking for link tags makes sense here, we need to know
        # a little more about the implementation. Whether HTML parser looks for 
        # the trailing slash at the end of an element, or just knows which elements
        # should be paired or not. 
        
        #print "found tag: %s" % tag
        if tag.lower() == 'link':
            print "Found link"
            if all (k in dattrs for k in ('rel', 'href', 'type')):
                if ( dattrs['rel'].lower() == 'stylesheet' and 
                     dattrs['type'].lower() == 'text/css' ):
                    #try to open the url...
                    self.linked_sheets.append(dattrs['href'])
                    
        # look for <style type='text/css' ... /> tags usually found in the head
        elif (tag.lower() == 'style' and 'type' in dattrs and
              dattrs['type'].lower() == 'text/css'):
            print "Found CSS inline defs"
            self.get_data = True
        self.append_styles(tag, attrs)
    
    def handle_data(self, data):
        """
        Called only for certain start tags where the data
        in the body of the tag is of interest. In this case, 
        the data is for <style> tags and <link> tags to css
        documents. 
        @param <string> data
            The data lying between an opening and closing HTML
            tag. For instance in <div>lorem impsum</div>, data 
            would be 'lorem ipsum'.
        """
        if self.get_data == True:
            self.inline_css_data.append(data)
            print self.inline_css_data
            print "Sending to parser"
            self.parse_inline_styles(data, 'string')
            self.get_data = False
        
    def handle_startendtag(self, tag, attrs):
        """
        Called when Cssparser finds a tag that does not have a
        closing tag, such as <meta>, or <link>. These tags have
        no data, so we just pass them forward.
        @param <string> tag
            The HTML tag we're currently parsing
        @param <tuple> attrs
           A tuple of HTML element attributes such as 'class', 'id',
           'style', etc. The tuple is of the form ('html_attribute',
           'attr1', 'attr2', 'attr3' ... 'attrN')
        """
        dattrs = dict(attrs)
        if tag.lower() == 'link':
            print "Found link"
            if all (k in dattrs for k in ('rel', 'href', 'type')):
                if ( dattrs['rel'].lower() == 'stylesheet' and 
                     dattrs['type'].lower() == 'text/css' ):
                    #try to open the url...
                    print "Trying to read %s"  % dattrs['href']
                    if dattrs['href'][:5].lower() == 'http:':
                        self.linked_sheets.append(dattrs['href'])
                    else:
                        self.linked_sheets.append(self.url_root+dattrs['href'])
        self.append_styles(tag, attrs)
    
    def append_styles(self, tag, attrs):
        dattrs = dict(attrs)
        if 'class' in dattrs:
            #print "Found classes '%s'" % dattrs['class']
            class_names = dattrs['class'].split()
            dotted_names = map(prepend_dot,class_names)
            dotted_names.sort()
            self.used_classes.extend(' '.join(dotted_names))
            self.unchained_classes.extend(dotted_names)
        if 'id' in dattrs:
            #print "Found id '%s'" % dattrs['id']
            self.used_ids.extend(prepend_hash(dattrs['id'].strip()))
            
            
    def parse_inline_styles(self, data=None, import_type ='string'):
        """
        Function for parsing styles defined in the body of the document. 
        This only includes data inside of HTML <style> tags, a URL, or file to open.
        """
        if data is None:
            raise
        parser = cssutils.CSSParser()
        if import_type == 'string':
            print "importing string with url=%s" % self.url_root
            sheet = parser.parseString(data,href=self.url_root)
        elif import_type == 'url':
            try:
                sheet = parser.parseUrl(data)
            except:
                print "WARNING: Failed attempting to parse %s" % data
                return
        elif import_type == 'file':
            sheet = parser.parseFile(data)
        else:
            raise

        hrefs = []
        for i in range(len(sheet.cssRules)):
            if sheet.cssRules[i].type == cssutils.css.CSSStyleRule.STYLE_RULE:
                selector = sheet.cssRules[i].selectorText
                #print "cssparser found  selector: %s" % selector
                selectors = selector.split(',')
                self.defined_classes.extend(selectors)

            elif ( self.follow_css_links == True and
                  sheet.cssRules[i].type == cssutils.css.CSSStyleRule.IMPORT_RULE ):
                href = sheet.cssRules[i].href
                print "Added %s to the stylesheets to crawl" % href
                # we'll have to try to add in a url root here, if these are relative
                # links.
                self.linked_sheets.append(self.url_root+href)
                self.parse_inline_styles(data=self.url_root+href, import_type='url')
            else:
                # we don't worry about these cases yet.
                pass
    
    

def prepend_char(char, word):
    return char + word

def prepend_dot(word):
    return prepend_char('.', word)

def prepend_hash(word):
    return prepend_char('#', word)

def extract_leftmost_selector(selector_list):
    classes = set()
    ids = set()
    elements = set()
    #    print "Selector list: %s \n\n\n\n\n\n" % selector_list
    for selector in selector_list:
        selector = selector.split()[0]
        if selector[0] == '.':
            classes.add(selector)
        elif selector[0] == '#':
            ids.add(selector)
        else:
            elements.add(selector)
    return { 
             'classes':classes,
             'ids':ids,
             'elements':elements,
             }


def main():
    from optparse import OptionParser
    opt_parser = OptionParser("usage: %prog [options] file url_root")
    opt_parser.add_option("-f", "--file", dest="filename",
                      help="The HTML source file to begin parsing")
    opt_parser.add_option("-u", "--url", dest="urlroot",
                      help="The URL Root of the site you are going to crawl")
    
    (options, args) = opt_parser.parse_args()
    if len(args) != 2:
        if opt_parser.filename is not None and opt_parser.urlroot is not None:
            urlroot = opt_parser.urlroot
            filename = opt_parser.filename
        else:
            opt_parser.error("Incorrect number of arguments")
    else:
        filename = args[0]
        urlroot = args[1]
    
    # must send a file to open!
    try:
        f = open(filename)
    except:
        print "Unable to open file %s for reading" % filename
        sys.exit(1)

    try:
        urllib2.urlopen(urlroot)
    except:
        print "Unable to open url %s for reading" % urlroot
        sys.exit(1)
    
    mycssauditor = Cssparser(f, urlroot)
    used_classes = set(mycssauditor.unchained_classes)
    used_ids = set(mycssauditor.used_ids)
    used_elements = set(mycssauditor.used_elements)
    defined_classes = extract_leftmost_selector(mycssauditor.defined_classes)['classes']
    print "Defined classes: %s \n\n\n\n\n" % defined_classes
    print "Used classes: %s \n\n\n\n\n\n" % used_classes
    print "These classes seem to have been defined but left unused:\n %s\n" % (
        defined_classes - used_classes
        )

if __name__ == '__main__':
    main()
