#! /usr/bin/env python
"""
CSS Audit
(C) Kyle Wanamaker, 2011
Licensed under the GNU General Public License version 3
Please see: http://www.gnu.org/licenses/ for the text of
the GPL v3. 

A copy of the GNU GPL v3 is included with the PyPi package
"""
import sys
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
        self.inline_css_data = []
        self.get_data = False
        self.follow_css_links = True
        self.url_root = urlroot
        # This is a hack because we don't build a tree; instead we have to
        # break the leftmost class and stick it in `unchained_classes`.
        self.unchained_classes = []
        self.used_ids = []
        self.used_elements = []
        
        # this line always goes last
        self.feed(fh.read())
        #print "Linked sheets %s " % self.linked_sheets
        for sheet in self.linked_sheets:
            #print "And the sheet is %s" % sheet,
            #print "Because linked_sheets is: %s " % self.linked_sheets
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
        
        if tag.lower() == 'link':
            print "Found link"
            if all (k in dattrs for k in ('rel', 'href', 'type')):
                if ( dattrs['rel'].lower() == 'stylesheet' and 
                     dattrs['type'].lower() == 'text/css' ):
                    # Add the url to the stack
                    if (dattrs['href'][:5].lower() == 'http:' or 
                       dattrs['href'][:6].lower() == 'https:'):
                        self.linked_sheets.append(dattrs['href'])
                    else:
                        self.linked_sheets.append(self.url_root+dattrs['href'])
                    
        # Look for <style type='text/css' ... /> tags and add their rules
        # into the list.
        elif (tag.lower() == 'style' and 
              'type' in dattrs and dattrs['type'].lower() == 'text/css'):
            #print "Found CSS inline defs"
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
            #print self.inline_css_data
            #print "Sending to parser"
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
            #print "Found link"
            if all (k in dattrs for k in ('rel', 'href', 'type')):
                if ( dattrs['rel'].lower() == 'stylesheet' and 
                     dattrs['type'].lower() == 'text/css' ):
                    #try to open the url...
                    #print "Trying to read %s"  % dattrs['href']
                    if (dattrs['href'][:5].lower() == 'http:' or 
                       dattrs['href'][:6].lower() == 'https:'):
                        self.linked_sheets.append(dattrs['href'])
                    else:
                        self.linked_sheets.append(self.url_root+dattrs['href'])
        self.append_styles(tag, attrs)
    
    def append_styles(self, tag, attrs):
        """
        Append classes found in HTML elements to the list of styles used.
        Because we haven't built the tree, we aren't using the `tag` parameter
        for now.
        @param <string> tag
            The HTML tag we're parsing
        @param <tuple> attrs
            A tuple of HTML element attributes such as 'class', 'id',
            'style', etc. The tuple is of the form ('html_attribute',
            'attr1', 'attr2', 'attr3' ... 'attrN')
        """
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
            #print "importing string with url=%s" % self.url_root
            sheet = parser.parseString(data,href=self.url_root)
        elif import_type == 'url':
          if data[:5].lower() == 'http:' or data[:6].lower() == 'https:':
            print "YES because it was: %s " % data[:5].lower()
            try:
                sheet = parser.parseUrl(data)
            except:
                sys.stderr.write("WARNING: Failed attempting to parse %s" % data)
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
                sys.stderr.write("Added %s to the stylesheets to crawl" % href)
                
                if href[:5].lower() == 'http:' or href[:6].lower() == 'https:':
                    self.linked_sheets.append(href)
                else:
                    # We'll have to try to add in a url root here, if these are relative
                    # links.
                    self.linked_sheets.append(self.url_root+href)
                    self.parse_inline_styles(data=self.url_root+href, import_type='url')
            else:
                # We won't worry about the other rule types.
                pass
    
    

def prepend_char(char, word):
    return char + word

def prepend_dot(word):
    return prepend_char('.', word)

def prepend_hash(word):
    return prepend_char('#', word)

def extract_leftmost_selector(selector_list):
    """
    Because we aren't building a DOM tree to transverse, the only way
    to get the most general selectors is to take the leftmost. 
    For example with `div.outer div.inner`, we can't tell if `div.inner`
    has been used in context without building a tree.
    """
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
    # We want to change this so that it can just accept a plain URL. 
    usage = """
            Usage: $ ./parser.py url
            Note: the url must be prefixed with the desired method 
            (either `http://` or `https://`)\n\n"""
    src = ''
    try:
      print sys.argv
      script, src = sys.argv
    except:
        sys.stderr.write("Incorrect number of arguments given.\n")
        sys.stderr.write(usage)
        sys.exit(1)

    req = urllib2.Request(src)
    urlroot = req.get_type() + '://' + req.get_host()
    try:
        f = urllib2.urlopen(req)
    except:
        sys.stderr.write("Unable to open url: %s for reading." % src)
        print(usage)
        sys.exit(1)
    
    mycssauditor = Cssparser(f, urlroot)
    
    # Use the `set` datatype since it will eliminate duplicate entries for us.
    used_classes = set(mycssauditor.unchained_classes)
    used_ids = set(mycssauditor.used_ids)
    used_elements = set(mycssauditor.used_elements)
    defined_classes = extract_leftmost_selector(mycssauditor.defined_classes)['classes']
    print "Defined classes: %s \n\n\n\n\n" % defined_classes
    print "Used classes: %s \n\n\n\n\n" % used_classes
    print "These classes seem to have been defined but left unused:\n %s\n" % (
        defined_classes - used_classes
        )

if __name__ == '__main__':
    main()
