# -*- coding: utf-8 -*-

import urllib2 as urllib
from django.conf import settings
import re


def copy_file(url, filename, slug):
    """
    Helper function to copy images from source
    """
    f = urllib.urlopen(url)
    destination = open(settings.MEDIA_ROOT + 'img/articles/'+ filename, 'wb+')
    destination.write(f.read())
    destination.close()
    f.close()



def clean_text(text):
	"""
	Strips special characters and other CCI/Workbench clutter from a string, and sends it back.
	"""
	for r in replacements:
		text = text.replace(r[0],r[1])
	return text


	
def workbench_to_markdown(para):
	"""
	Turns Workbench's ridiculous translation of Newsgate XML into Markdown. Order matters.
	"""
	# Strip extraneous spaces around tags
	para = para.replace('&lt;','<').replace('&gt;','>')
	para = para.replace(' <','<').replace('> ','>') 

	# This is a problem, because if there's a tag inside the subhead, it won't match.
	para = re.sub(r'<span class="subhead">(?P<stuff>[^<]*)</span>', '\n\n### \g<1> ', para) 

	# handle bold and italics
	para = re.sub(r'<span class="bold">(?P<stuff>[^<]*)</span>', ' **\g<1>** ', para) 
	para = re.sub(r'<span class="italic">(?P<stuff>[^<]*)</span>', ' *\g<1>* ', para) 

	# Strip any extra elements, add newlines between paragraphs
	para = re.sub(r'<[^>]*?>', '', para) 
	# Toss extra whitespace. Condenses the totally-stripped tags to empty strings.
	para = para.strip() 
	# If we're empty, toss it
	if not para: 
		return False
	# Otherwise, make sure it ends with two newlines
	if para[len(para)-2:] != '\n\n':
		para = para + "\n\n"
	return para
	

# replacements are done in order (for r in replacements: replace(r[0],r[1])) so you can replace, then replace again
replacements = [
	("&amp;"        , '&'),

	('&#x97;'       , '--'),
	('&#x2014;'     , "--"),
	('&#x2013;'     , "--"),
	#('&amp;#x2014;' , "--"),
	('&mdash;'      , '--'),
	("&#8212;"      , '--'),
	('&lt;p/&gt;'   , '\n\n'),
	('<p/>'         , '\n\n'),
	('<p></p>'      , '\n\n'),
	# single quotes
	('&#x2018;'     , "'"),
	('&#x2019;'     , "'"),
	('&#39;'        , "'"),
	('&#x91;'       , "'"),
	('&#x92;'       , "'"),
	('&#xD5;'       , "'"),
	('&#8217;'      , "'"),
	("&#8216;"      , "'"),
	# double quotes
	('&#x93;'       , '"'),
	('&#x94;'       , '"'),
	('&#x201C;'     , '"'),
	('&#x201c;'     , '"'),
	('&#x201C;'     , '"'),
	('&#x201D;'     , '"'),
	('&#x201d;'     , '"'),
	('&#xD2;'       , '"'),
	('&#xD3;'       , '"'),
	('&quot;'       , '"'),
	("&#8220;"      , '"'),
	("&#8221;"      , '"'),
	# other stuff
	#('&#xC1;'       , 'Á'), # accented A
	('&#x85;'       , '...'),
	('&#8230;'      , '...'),
	('&#x2026;'     , '...'),
	
	
	# newsgate nonsense
	("&#8199;"      , ""), # spacer character from newsgate)
	("&bull;&nbsp;" , '* '),
	("&bull;&#xA0;" , '* '),
	#("&#189;"       , '½'),
	
	# this is some crap CCI Newsdesk inserted.
	# if Newsgate doesn't, we'll be able to remove this mess...
	('&lt;hr class="infobox-hr-separator"'            , ''),
	('/&gt; &lt;div class="infobox"&gt; &lt;/div&gt;' , ''),
	('<cci:z_sym_square_bullet class="macro" displayname="bullet" name="z_sym_square_bullet"/>', '&bull;'),

	# superscripts
	('{+t}'         , 't'),
	('{+h}'         , 'h'),
]


# Old version
# replacements = {
# 	"&amp;"	      : '&',

# 	'&#x97;'       : '--',
# 	'&#x2014;'     : "--",
# 	#'&amp;#x2014;' : "--",
# 	'&mdash;'      : '--',
# 	"&#8212;"      : '--',
# 	'&lt;p/&gt;'   : '\n\n',
# 	'<p/>'         : '\n\n',
# 	'<p></p>'      : '\n\n',
# 	# single quotes
# 	'&#x2018;'     : "'",
# 	'&#x2019;'     : "'",
# 	#'&amp;#x2019;' : "'",
# 	'&#39;'        : "'",
# 	'&#x91;'       : "'",
# 	'&#x92;'       : "'",
# 	#'&amp;#x92;'   : "'",
# 	'&#xD5;'       : "'",
# 	'&#8217;'      : "'",
# 	"&#8216;"      : "'", 
# 	# double quotes
# 	'&#x93;'       : '"',
# 	#'&amp;#x93;'   : '"',
# 	'&#x94;'       : '"',
# 	#'&amp;#x94;'   : '"',
# 	'&#x201C;'     : '"',
# 	#'&amp;#x201C;' : '"',
# 	'&#x201c;'     : '"',
# 	'&#x201C;'     : '"',
# 	'&#x201D;'     : '"',
# 	#'&amp;#x201D;' : '"',
# 	'&#x201d;'     : '"',
# 	'&#xD2;'       : '"',
# 	'&#xD3;'       : '"',
# 	'&quot;'       : '"',
# 	"&#8220;"      : '"', 
# 	"&#8221;"      : '"', 
# 	# other stuff
# 	'&#xC1;'       : 'Á',    # accented A
# 	'&#x85;'       : '...',
# 	#'&amp;#x85;'   : '...',
# 	"&#8199;"      : "",     # spacer character from newsgate

# 	# this is some crap CCI Newsdesk inserted.
# 	# if Newsgate doesn't, we'll be able to remove this mess...
# 	'&lt;hr class="infobox-hr-separator"'            : '',
# 	'/&gt; &lt;div class="infobox"&gt; &lt;/div&gt;' : '',
# }
