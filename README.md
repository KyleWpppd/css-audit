CSS AUDIT
=========

### For when there is just too much css to go through ###

**Usage**
`$ parser.py html-file.html urlroot`
Where `html-file.html` is on your local system, and `urlroot` is the `http://`-prefixed site you want to crawl. 

Right now, to crawl, you would use

    $ wget http://www.example.com -O index.html
    $ ./parser.py index.html http://www.example.com


This is rather basic and the moment and will be improved in upcoming versions. Full website parsing with depth is one of the upcoming features. 


What it is (Features)
---------------------
**CSS Audit** is a python-based tool to make it easy to figure out which stylesheets and style rules you may or may not be using across your website. 

**CSS Audit** will crawl your site and take an inventory of every CSS class and id used, and compare it to those you have defined in your stylesheets.

**CSS Audit** does not know anything about JavaScript or dynamically added classes. 

What it isn't
-------------
**CSS Audit** is not a browser, it does nothing with JavaScript, so if you are using JS to add and remove classes CSS Audit will probably get it wrong. 

Author
------
Copyright (c) 2011
Kyle Wanamaker

@KyleWpppd
www.klowell.com
kyle [at] klowell [dot] com

License
-------
GNU GPL v3

Please see the attached license file for more information.
