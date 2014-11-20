from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.utils import safestring
from django.contrib.sites.models import Site
from blogs.models import Entry, Image, Blog
from django.conf import settings

import feedparser
import urllib

site = Site.objects.get_current()

def copy_file(url, filename, slug):
    f = urllib.urlopen(url).read()
    destination = open(settings.MEDIA_ROOT + 'img/blogs/' + slug + '/'+ filename, 'wb+')
    destination.write(f)
    destination.close()
    
def create_blog(title):
    """
    Helper function to create blog if it doesn't already exist
    """
    blog = Blog(
    	title     = title,
    	slug      = slugify(title),
    	summary   = '',
    	site      = site,
    )
    
    blog.save()
    return blog
    
        
def from_feed(source):
	"""
	Imports blog entries from an external site via RSS.
	"""
	status = 'attempting to import from feed %s<br>' % source.feed_url 
	d = feedparser.parse(source.feed_url)
	
	# Match to blog
	try:
		blog = Blog.objects.get(title=source.title)
	except:
		blog = create_blog(source.title)
		
	for item in d.entries:
		dupe = False            # Set our dupe flag for the following loop
		try:
			existing = Entry.objects.get(title=item.title) 
			dupe = True
		except:		
			if dupe==False:
				cleanbody = strip_tags(item.description).replace('\n', '\n\n')
				try:
					i = Entry(
					   title     = item.title,
					   slug      = slugify(item.title),
				   	blog      = blog,
					   summary   = cleanbody[:200].rsplit(' ', 1)[0]+'...',
					   body      = item.description,
					   published = True
					)
					i.save()
				except:
					pass
				if item.has_key('media_content'):
					for m in item.media_content:			
						url = m['url']
						try:
							caption = item.media_description
						except:
							caption = '';
						filename = url.rsplit('/', 1)[1]
						copy_file(url, filename, blog.slug)
						img = Image(image="img/blogs/"+ blog.slug + '/' + filename, caption= caption, entry=i)
						img.save()  

	status += "done"